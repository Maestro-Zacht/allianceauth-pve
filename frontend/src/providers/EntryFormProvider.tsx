import { createContext, useContext, useEffect, useReducer, type Dispatch, type PropsWithChildren } from "react";
import type { ExtendedEntryFormSchema } from "../components/entries/EntryTypes";

type RoleType = ExtendedEntryFormSchema["roles"][number];

const EntryFormUpdateContext = createContext<EntryProcessorType | undefined>(undefined);
const EntryFormDataContext = createContext<ExtendedEntryFormSchema | undefined>(undefined);

type EntryReducerAction =
    | { type: 'update_estimated_total'; estimated_total: number }
    | { type: 'increment_estimated_total'; increment: number }
    | { type: 'add_role'; role: RoleType }
    | { type: 'load_role_setup'; roles: RoleType[] }
    | { type: 'update_role_value'; roleName: string; value: number }
    | { type: 'delete_role'; roleName: string }
    | { type: 'update_shares'; onlyPresent: boolean; increment: number }
    | { type: 'select_funding_project'; projectId: number | null }
    | { type: 'update_funding_percentage'; percentage: number }
    | { type: 'add_character'; characterId: number, characterName: string, portraitUrl: string, mainCharacterName: string, mainCharacterPortraitUrl: string }
    | { type: 'toggle_share_value'; characterId: number, field: 'helped_setup' | 'is_present' }
    | { type: 'change_share_role'; characterId: number; newRoleName: string }
    | { type: 'update_share_count'; characterId: number; value: number }
    | { type: 'delete_share'; characterId: number };

function entryFormDataReducer(state: ExtendedEntryFormSchema, action: EntryReducerAction): ExtendedEntryFormSchema {
    switch (action.type) {
        case 'update_estimated_total':
            return { ...state, estimated_total: action.estimated_total };
        case 'increment_estimated_total':
            return { ...state, estimated_total: state.estimated_total + action.increment };
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
        case 'delete_role':
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
        case "update_funding_percentage":
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
        case "add_character":
            if (state.shares.some(share => share.character_id === action.characterId)) {
                return state;
            }
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
                        site_count: 1,
                        helped_setup: false,
                        is_present: true,
                    }
                ]
            };
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
};

interface EntryFormProviderProps {
    initialData: ExtendedEntryFormSchema;
    submitEntry: (data: ExtendedEntryFormSchema) => void;
}

export function EntryFormProvider({ initialData, submitEntry, children }: PropsWithChildren<EntryFormProviderProps>) {
    const [entryData, dispatchEntryData] = useReducer(entryFormDataReducer, initialData);

    useEffect(() => {
        if (initialData.roles.length === 0) {
            dispatchEntryData({ type: 'add_role', role: { name: "Krab", value: 1 } });
        }
    }, []);

    const submitAction = () => {
        submitEntry(entryData);
    };

    const entryProcessor: EntryProcessorType = {
        updateEntryData: dispatchEntryData,
        submitEntry: submitAction,
    };

    return <>
        <EntryFormDataContext.Provider value={entryData}>
            <EntryFormUpdateContext.Provider value={entryProcessor}>
                {children}
            </EntryFormUpdateContext.Provider>
        </EntryFormDataContext.Provider>
    </>
}

export function useEntryProcessor() {
    const context = useContext(EntryFormUpdateContext);
    if (context === undefined) {
        throw new Error('useEntryProcessor must be used within an EntryFormProvider');
    }
    return context;
}

export function useEntryFormData() {
    const context = useContext(EntryFormDataContext);
    if (context === undefined) {
        throw new Error('useEntryFormData must be used within an EntryFormProvider');
    }
    return context;
}