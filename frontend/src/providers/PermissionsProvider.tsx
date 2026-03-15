import { createContext, useContext, type ReactNode } from "react";
import type { components } from "../api/Schema";
import { useQuery } from "@tanstack/react-query";
import { getUserPermissions } from "../api/api";

type PermissionsType = components["schemas"]["PermissionsSchema"];

const PermissionsContext = createContext<PermissionsType | undefined | null>(null);

export function PermissionsProvider({ children }: { children: ReactNode }) {
    const { data, error } = useQuery({
        queryKey: ['permissions'],
        queryFn: getUserPermissions,
    });

    if (error) {
        console.error("Error loading permissions:", error);
        return <div>Error loading permissions.</div>;
    }

    return <>
        <PermissionsContext.Provider value={data}>
            {children}
        </PermissionsContext.Provider>
    </>
}

export function usePermissions() {
    const context = useContext(PermissionsContext);
    if (context === null) {
        throw new Error('usePermissions must be used within a PermissionsProvider');
    }
    return context;
}