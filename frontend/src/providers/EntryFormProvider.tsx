import { createContext, useContext, useEffect, type Dispatch, type PropsWithChildren } from "react";
import type { ExtendedEntryFormSchema, ExtendedEntryItem, SiteRange, SiteScaling } from "../components/entries/EntryTypes";
import { isCompleteRange, mergeSiteRanges, shareLastSite } from "../components/entries/siteRanges";
import { useLocalStorageReducer } from "../hooks/useLocalStorageReducer";

type RoleType = ExtendedEntryFormSchema["roles"][number];
type ShareType = ExtendedEntryFormSchema["shares"][number];

function currentFleetSite(shares: ShareType[]): number {
    return Math.max(0, ...shares.map(shareLastSite));
}

/** Start an active range at `start`, reopening the last past range when the new one would overlap or touch it. */
function openActiveRange(share: ShareType, start: number): ShareType {
    const lastPast = share.sites.at(-1);
    if (lastPast && start <= lastPast.last + 1) {
        return {
            ...share,
            sites: share.sites.slice(0, -1),
            active_sites: { first: lastPast.first, last: Math.max(lastPast.last, start) },
        };
    }
    return { ...share, active_sites: { first: start, last: start } };
}

function updateShare(shares: ShareType[], characterId: number, update: (share: ShareType) => ShareType): ShareType[] {
    return shares.map(share => share.character_id === characterId ? update(share) : share);
}

const EntryFormUpdateContext = createContext<EntryProcessorType | undefined>(undefined);
const EntryFormDataContext = createContext<ExtendedEntryFormSchema | undefined>(undefined);

type EntryReducerAction =
    | { type: 'update_estimated_total'; estimated_total: number }
    | { type: 'increment_estimated_total'; increment: number }
    | { type: 'add_items'; items: ExtendedEntryItem[] }
    | { type: 'replace_items'; items: ExtendedEntryItem[] }
    | { type: 'update_item_quantity'; item_id: number; quantity: number }
    | { type: 'delete_item'; item_id: number }
    | { type: 'add_role'; role: RoleType }
    | { type: 'load_role_setup'; roles: RoleType[] }
    | { type: 'update_role_value'; roleName: string; value: number }
    | { type: 'delete_role'; roleName: string }
    | { type: 'update_shares'; increment: number }
    | { type: 'select_funding_project'; projectId: number | null }
    | { type: 'update_funding_percentage'; percentage: number }
    | { type: 'select_site_scaling'; siteScaling: SiteScaling }
    | { type: 'add_character'; characterId: number, characterName: string, portraitUrl: string, mainCharacterName: string, mainCharacterPortraitUrl: string }
    | { type: 'toggle_share_value'; characterId: number, field: 'helped_setup' }
    | { type: 'change_share_role'; characterId: number; newRoleName: string }
    | { type: 'update_active_site'; characterId: number; field: 'first' | 'last'; value: number }
    | { type: 'open_active_range'; characterId: number }
    | { type: 'close_active_range'; characterId: number }
    | { type: 'update_past_ranges'; characterId: number; ranges: SiteRange[]; reopenLast: boolean }
    | { type: 'delete_share'; characterId: number };

function entryFormDataReducer(state: ExtendedEntryFormSchema, action: EntryReducerAction): ExtendedEntryFormSchema {
    switch (action.type) {
        case 'update_estimated_total':
            return { ...state, estimated_total: action.estimated_total };
        case 'increment_estimated_total':
            return { ...state, estimated_total: state.estimated_total + action.increment };
        case 'add_items': {
            const newItemMap = new Map<number, ExtendedEntryItem>();
            for (const item of [...action.items, ...state.items]) {
                const existingItem = newItemMap.get(item.id) || { ...item, quantity: 0 };
                existingItem.quantity += item.quantity;
                newItemMap.set(item.id, existingItem);
            }
            return { ...state, items: Array.from(newItemMap.values()).map(item => item.quantity < 1 ? { ...item, quantity: 1 } : item) };
        }
        case 'replace_items':
            return { ...state, items: action.items.map(item => item.quantity < 1 ? { ...item, quantity: 1 } : item) };
        case 'update_item_quantity':
            if (isNaN(action.quantity) || action.quantity < 1) {
                return state;
            }
            return {
                ...state,
                items: state.items.map(item =>
                    item.id === action.item_id ? { ...item, quantity: action.quantity } : item
                )
            };
        case 'delete_item':
            return { ...state, items: state.items.filter(item => item.id !== action.item_id) };
        case 'add_role':
            if (state.roles.some(role => role.name === action.role.name)) {
                return state;
            }
            return { ...state, roles: [...state.roles, action.role] };
        case 'load_role_setup': {
            if (action.roles.length === 0) {
                return state;
            }
            const roleNames = new Set(action.roles.map(role => role.name));
            return {
                ...state,
                roles: action.roles,
                shares: state.shares.map(share => roleNames.has(share.role_name) ?
                    share :
                    { ...share, role_name: action.roles[0].name }
                )
            };
        }
        case 'update_role_value':
            return {
                ...state,
                roles: state.roles.map(
                    role => role.name === action.roleName ?
                        { ...role, value: action.value } :
                        role
                )
            };
        case 'delete_role': {
            const fallbackRole = state.roles.find(role => role.name !== action.roleName);
            if (state.roles.length === 1 || !fallbackRole) {
                return state;
            }
            return {
                ...state,
                roles: state.roles.filter(role => role.name !== action.roleName),
                shares: state.shares.map(
                    share => share.role_name === action.roleName ?
                        { ...share, role_name: fallbackRole.name } :
                        share
                )
            };
        }
        case 'update_shares': {
            const fleetSite = currentFleetSite(state.shares);
            return {
                ...state,
                shares: state.shares.map(share => {
                    const active = share.active_sites;
                    if (active === null) {
                        return share;
                    }
                    if (active.first === null && active.last === null) {
                        return action.increment > 0 ?
                            openActiveRange(share, fleetSite + 1) :
                            share;
                    }
                    if (active.last === null) {
                        return action.increment > 0 ?
                            { ...share, active_sites: { ...active, last: active.first } } :
                            share;
                    }
                    const newLastSite = active.last + action.increment;
                    return {
                        ...share,
                        active_sites: { ...active, last: newLastSite < (active.first ?? 1) ? null : newLastSite },
                    };
                })
            };
        }
        case "select_funding_project":
            return {
                ...state,
                funding_project_id: action.projectId,
                funding_percentage: action.projectId === null ?
                    null :
                    state.funding_percentage === null ?
                        1 :
                        state.funding_percentage
            };
        case "update_funding_percentage": {
            if (state.funding_project_id === null) {
                return state;
            }

            let newPercentage = action.percentage;
            if (newPercentage < 1) {
                newPercentage = 1;
            } else if (newPercentage > 100) {
                newPercentage = 100;
            }

            return {
                ...state,
                funding_percentage: newPercentage
            };
        }
        case "select_site_scaling":
            return {
                ...state,
                site_scaling: action.siteScaling,
            };
        case "add_character": {
            if (state.shares.some(share => share.character_id === action.characterId)) {
                return state;
            }
            const startSite = Math.max(currentFleetSite(state.shares), 1);
            return {
                ...state,
                shares: [
                    ...state.shares,
                    {
                        character_id: action.characterId,
                        character_name: action.characterName,
                        portrait_url: action.portraitUrl,
                        main_character_name: action.mainCharacterName,
                        main_character_portrait_url: action.mainCharacterPortraitUrl,
                        role_name: state.roles[0].name,
                        sites: [],
                        active_sites: { first: startSite, last: startSite },
                        helped_setup: false,
                    }
                ]
            };
        }
        case "toggle_share_value":
            return {
                ...state,
                shares: state.shares.map(share => {
                    if (share.character_id === action.characterId) {
                        return { ...share, [action.field]: !share[action.field] };
                    } else {
                        return share;
                    }
                })
            };
        case "change_share_role":
            if (!state.roles.some(role => role.name === action.newRoleName)) {
                return state;
            }
            return {
                ...state,
                shares: state.shares.map(share => {
                    if (share.character_id === action.characterId) {
                        return { ...share, role_name: action.newRoleName };
                    } else {
                        return share;
                    }
                })
            };
        case "update_active_site":
            return {
                ...state,
                shares: updateShare(state.shares, action.characterId, share => {
                    if (share.active_sites === null) {
                        return share;
                    }
                    const newSite = isNaN(action.value) ? null : Math.max(action.value, 1);
                    return { ...share, active_sites: { ...share.active_sites, [action.field]: newSite } };
                })
            };
        case "open_active_range": {
            const startSite = Math.max(currentFleetSite(state.shares), 1);
            return {
                ...state,
                shares: updateShare(state.shares, action.characterId, share =>
                    share.active_sites === null ? openActiveRange(share, startSite) : share
                )
            };
        }
        case "close_active_range":
            return {
                ...state,
                shares: updateShare(state.shares, action.characterId, share => {
                    const active = share.active_sites;
                    if (isCompleteRange(active)) {
                        if (active.last < active.first) {
                            return share;
                        }
                        return { ...share, sites: mergeSiteRanges([...share.sites, active]), active_sites: null };
                    }
                    return { ...share, active_sites: null };
                })
            };
        case "update_past_ranges":
            return {
                ...state,
                shares: updateShare(state.shares, action.characterId, share => {
                    const sites = mergeSiteRanges(action.ranges);
                    const lastPast = sites.at(-1);
                    const active = share.active_sites;
                    if (lastPast === undefined) {
                        return { ...share, sites };
                    }
                    if (active !== null && active.first !== null && lastPast.last + 1 >= active.first) {
                        return { ...share, sites: sites.slice(0, -1), active_sites: { ...active, first: lastPast.first } };
                    }
                    if (action.reopenLast && active === null) {
                        return { ...share, sites: sites.slice(0, -1), active_sites: { ...lastPast } };
                    }
                    return { ...share, sites };
                })
            };
        case "delete_share":
            return {
                ...state,
                shares: state.shares.filter(share => share.character_id !== action.characterId)
            };
        default:
            return state;
    }
}

type EntryProcessorType = {
    updateEntryData: Dispatch<EntryReducerAction>;
    submitEntry: () => void;
    resetLocalStorage: () => void;
};

interface EntryFormProviderProps {
    initialData: ExtendedEntryFormSchema;
    localStorageKey?: string | null | undefined;
    submitEntry: (data: ExtendedEntryFormSchema, resetFunction: () => void) => void;
}

export function EntryFormProvider({ initialData, localStorageKey, submitEntry, children }: PropsWithChildren<EntryFormProviderProps>) {
    const [entryData, dispatchEntryData, resetLocalStorage] = useLocalStorageReducer(localStorageKey ?? null, entryFormDataReducer, initialData);

    useEffect(() => {
        if (initialData.roles.length === 0) {
            dispatchEntryData({ type: 'add_role', role: { name: "Krab", value: 1 } });
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps -- run once on mount to seed the default role
    }, []);

    const submitAction = () => {
        submitEntry(entryData, resetLocalStorage);
    };

    const entryProcessor: EntryProcessorType = {
        updateEntryData: dispatchEntryData,
        submitEntry: submitAction,
        resetLocalStorage: resetLocalStorage,
    };

    return <>
        <EntryFormDataContext.Provider value={entryData}>
            <EntryFormUpdateContext.Provider value={entryProcessor}>
                {children}
            </EntryFormUpdateContext.Provider>
        </EntryFormDataContext.Provider>
    </>
}

// eslint-disable-next-line react-refresh/only-export-components -- hook co-located with its provider
export function useEntryProcessor() {
    const context = useContext(EntryFormUpdateContext);
    if (context === undefined) {
        throw new Error('useEntryProcessor must be used within an EntryFormProvider');
    }
    return context;
}

// eslint-disable-next-line react-refresh/only-export-components -- hook co-located with its provider
export function useEntryFormData() {
    const context = useContext(EntryFormDataContext);
    if (context === undefined) {
        throw new Error('useEntryFormData must be used within an EntryFormProvider');
    }
    return context;
}
