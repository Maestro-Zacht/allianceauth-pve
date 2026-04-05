import { createContext, useContext, useReducer, type Dispatch, type PropsWithChildren } from "react";
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
    | { type: 'update_shares'; onlyPresent: boolean; increment: number };

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
                    if (share.isPresent || !action.onlyPresent) {
                        const newSiteCount = share.site_count + action.increment;
                        return {
                            ...share,
                            site_count: newSiteCount < 0 ? 0 : newSiteCount
                        }
                    } else {
                        return share;
                    }
                })
            }
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