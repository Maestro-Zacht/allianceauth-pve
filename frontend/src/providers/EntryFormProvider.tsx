import { createContext, useContext, useEffect, type Dispatch, type PropsWithChildren } from "react";
import type { EntryMode, ExtendedEntryFormSchema, ExtendedEntryItem, RampancyLevel } from "../components/entries/EntryTypes";
import { computeWaveCounts, DEFAULT_RAMPANCY_LEVEL } from "../components/entries/entry_form/waveShares";
import { useLocalStorageReducer } from "../hooks/useLocalStorageReducer";

type RoleType = ExtendedEntryFormSchema["roles"][number];

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
    | { type: 'update_shares'; onlyPresent: boolean; increment: number }
    | { type: 'set_mode'; mode: EntryMode }
    | { type: 'set_rampancy_level'; level: RampancyLevel }
    | { type: 'update_share_wave'; characterId: number; field: 'start_wave' | 'end_wave'; value: number }
    | { type: 'select_funding_project'; projectId: number | null }
    | { type: 'update_funding_percentage'; percentage: number }
    | { type: 'add_character'; characterId: number, characterName: string, portraitUrl: string, mainCharacterName: string, mainCharacterPortraitUrl: string }
    | { type: 'toggle_share_value'; characterId: number, field: 'helped_setup' | 'is_present' }
    | { type: 'change_share_role'; characterId: number; newRoleName: string }
    | { type: 'update_share_count'; characterId: number; value: number }
    | { type: 'delete_share'; characterId: number };

// In "fabs" mode each share's `site_count` is derived from its start/end wave
// via the wave-weighted formula, so it is recomputed whenever the roster or a
// wave range changes. In "sites" mode `site_count` is edited directly and this
// is a no-op.
function recountWaves(state: ExtendedEntryFormSchema): ExtendedEntryFormSchema {
    if (state.mode !== 'fabs') {
        return state;
    }
    const counts = computeWaveCounts(state.shares, state.rampancy_level ?? DEFAULT_RAMPANCY_LEVEL);
    return {
        ...state,
        shares: state.shares.map(share => ({
            ...share,
            site_count: counts[share.character_id] ?? 0,
        })),
    };
}

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
        case 'load_role_setup':
            if (action.roles.length === 0) {
                return state;
            }
            return {
                ...state,
                roles: action.roles,
                shares: state.shares.map(share => ({ ...share, role_name: action.roles[0].name }))
            };
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
        case 'update_shares':
            return {
                ...state,
                shares: state.shares.map(share => {
                    if (share.is_present || !action.onlyPresent) {
                        const newSiteCount = share.site_count + action.increment;
                        return {
                            ...share,
                            site_count: newSiteCount < 0 ? 0 : newSiteCount
                        }
                    } else {
                        return share;
                    }
                })
            };
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
        case "set_mode": {
            if (action.mode === state.mode) {
                return state;
            }
            if (action.mode === 'fabs') {
                return recountWaves({
                    ...state,
                    mode: 'fabs',
                    shares: state.shares.map(share => ({
                        ...share,
                        start_wave: share.start_wave ?? 1,
                        end_wave: share.end_wave ?? 1,
                    })),
                });
            }
            return {
                ...state,
                mode: 'sites',
                // Leaving fabs: hand the count back to the user; keep the wave
                // ranges so toggling back restores them. Normalising a missing
                // mode must not touch existing counts.
                shares: state.mode === 'fabs'
                    ? state.shares.map(share => ({ ...share, site_count: 1 }))
                    : state.shares,
            };
        }
        case "set_rampancy_level": {
            if (action.level === state.rampancy_level) {
                return state;
            }
            return recountWaves({ ...state, rampancy_level: action.level });
        }
        case "update_share_wave": {
            const value = isNaN(action.value) ? 1 : Math.max(1, Math.trunc(action.value));
            return recountWaves({
                ...state,
                shares: state.shares.map(share =>
                    share.character_id === action.characterId
                        ? { ...share, [action.field]: value }
                        : share
                )
            });
        }
        case "add_character": {
            if (state.shares.some(share => share.character_id === action.characterId)) {
                return state;
            }
            return recountWaves({
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
                        site_count: 1,
                        helped_setup: false,
                        is_present: true,
                        start_wave: 1,
                        end_wave: 1,
                    }
                ]
            });
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
        case "update_share_count":
            return {
                ...state,
                shares: state.shares.map(share => {
                    if (share.character_id === action.characterId) {
                        const newSiteCount = (action.value < 0 || isNaN(action.value)) ? 0 : action.value;
                        return { ...share, site_count: newSiteCount };
                    } else {
                        return share;
                    }
                })
            };
        case "delete_share":
            return recountWaves({
                ...state,
                shares: state.shares.filter(share => share.character_id !== action.characterId)
            });
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
        // Drafts persisted before the Sites/Fabs toggle existed have no `mode`.
        if (entryData.mode !== 'sites' && entryData.mode !== 'fabs') {
            dispatchEntryData({ type: 'set_mode', mode: 'sites' });
        }
        if (!entryData.rampancy_level) {
            dispatchEntryData({ type: 'set_rampancy_level', level: DEFAULT_RAMPANCY_LEVEL });
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps -- run once on mount to seed defaults
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
