import apiClient from "./ApiClient";
import type { paths, components } from "./Schema";
import type { FetchOptions } from "openapi-fetch";

type GetPaths = {
    [K in keyof paths]: 'get' extends keyof paths[K]
    ? [NonNullable<paths[K]["get"]>] extends [never]
    ? never
    : K
    : never;
}[keyof paths];

type ConditionallyOptional<T> = {} extends T ? [options?: T] : [options: T];

async function genericGet<Path extends GetPaths>(
    url: Path,
    ...options: ConditionallyOptional<FetchOptions<paths[Path]["get"]>>
) {
    const fetchOptions = options[0] as FetchOptions<paths[Path]["get"]>;
    const { data, error, response } = await apiClient.GET(url, fetchOptions);
    if (error) {
        console.error(`Error fetching ${String(url)}:`, error);
        throw error;
    }
    if (!response.ok) {
        console.error(`Error response ${response.status} fetching ${String(url)}`);
        throw response.status;
    }
    return data as NonNullable<typeof data>;
}

export async function getUserPermissions() {
    return await genericGet("/pve/api/permissions/");
}

export async function getUserPastActivity(months: number) {
    return await genericGet(
        "/pve/api/activity/months/{months}/",
        { params: { path: { months } } }
    );
}

export async function getRotationList() {
    return await genericGet("/pve/api/rotations/");
}

export async function getRotation(rotationId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/",
        { params: { path: { rotation_id: rotationId } } }
    );
}

export async function getProjectList() {
    return await genericGet("/pve/api/projects/");
}

export async function getRotationSummary(rotationId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/summary/",
        { params: { path: { rotation_id: rotationId } } }
    );
}

export async function getRotationEntries(rotationId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/entries/",
        { params: { path: { rotation_id: rotationId } } }
    );
}

export async function getRotationProjectsSummaries(rotationId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/project_summaries/",
        { params: { path: { rotation_id: rotationId } } }
    );
}

export async function getEntry(rotationId: number, entryId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/entries/{entry_id}/",
        { params: { path: { rotation_id: rotationId, entry_id: entryId } } }
    );
}

export async function getEntryRoles(rotationId: number, entryId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/entries/{entry_id}/roles/",
        { params: { path: { rotation_id: rotationId, entry_id: entryId } } }
    );
}

export async function getEntryShares(rotationId: number, entryId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/entries/{entry_id}/shares/",
        { params: { path: { rotation_id: rotationId, entry_id: entryId } } }
    );
}

export async function deleteEntry(rotationId: number, entryId: number) {
    const { error } = await apiClient.DELETE(
        "/pve/api/rotations/{rotation_id}/entries/{entry_id}/",
        { params: { path: { rotation_id: rotationId, entry_id: entryId } } }
    );
    if (error) {
        throw error;
    }
}

export async function getProjectDetails(projectId: number) {
    return await genericGet(
        "/pve/api/projects/{project_id}/",
        { params: { path: { project_id: projectId } } }
    );
}

export async function getProjectSummary(projectId: number) {
    return await genericGet(
        "/pve/api/projects/{project_id}/summary/",
        { params: { path: { project_id: projectId } } }
    );
}

export async function toggleProjectComplete(projectId: number) {
    const { error } = await apiClient.POST(
        "/pve/api/projects/{project_id}/complete/",
        { params: { path: { project_id: projectId } } }
    );
    if (error) {
        throw error;
    }
}

export async function getPveButtons() {
    return await genericGet("/pve/api/buttons/");
}

export async function getRoleSetups() {
    return await genericGet("/pve/api/role_setups/");
}

export async function createRotation(rotationData: components["schemas"]["NewRotationSchema"]) {
    const { data, error } = await apiClient.POST(
        "/pve/api/rotations/",
        { body: rotationData }
    );
    if (error) {
        throw error;
    }
    return data;
}

export async function createProject(projectData: components["schemas"]["NewProjectSchema"]) {
    const { data, error } = await apiClient.POST(
        "/pve/api/projects/",
        { body: projectData }
    );
    if (error) {
        throw error;
    }
    return data;
}

export async function closeRotation(rotationId: number, closeData: components["schemas"]["CloseRotationSchema"]) {
    const { error, response } = await apiClient.PATCH(
        "/pve/api/rotations/{rotation_id}/",
        {
            params: { path: { rotation_id: rotationId } },
            body: closeData
        }
    );
    if (error) {
        throw error;
    }
    if (!response.ok) {
        throw response.status;
    }
}

export async function createEntry(rotationId: number, entryData: components["schemas"]["EntryFormSchema"]) {
    const { error, response } = await apiClient.POST(
        "/pve/api/rotations/{rotation_id}/entries/",
        {
            params: { path: { rotation_id: rotationId } },
            body: entryData
        }
    );
    if (error) {
        throw error;
    }
    if (!response.ok) {
        throw response.status;
    }
}

export async function getRotationRoleSetups(rotationId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/role_setups/",
        { params: { path: { rotation_id: rotationId } } }
    );
}

export async function getRotationButtons(rotationId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/buttons/",
        { params: { path: { rotation_id: rotationId } } }
    );
}

export async function getActiveProjects() {
    return await genericGet(
        "/pve/api/projects/",
        { params: { query: { active: true } } }
    );
}

export async function searchRatters(name?: string | undefined, excludeIds?: number[] | undefined) {
    const { data, error } = await apiClient.POST(
        "/pve/api/search/ratters/",
        {
            params: { query: { name } },
            body: excludeIds,
        }
    );
    if (error) {
        throw error;
    }
    return data;
}

export async function getEntryEditData(rotationId: number, entryId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/entries/{entry_id}/edit/",
        { params: { path: { rotation_id: rotationId, entry_id: entryId } } }
    );
}

export async function editEntry(rotationId: number, entryId: number, entryData: components["schemas"]["EntryFormSchema"]) {
    const { error, response } = await apiClient.POST(
        "/pve/api/rotations/{rotation_id}/entries/{entry_id}/",
        {
            params: { path: { rotation_id: rotationId, entry_id: entryId } },
            body: entryData
        }
    );
    if (error) {
        throw error;
    }
    if (!response.ok) {
        throw response.status;
    }
}

export async function searchItems(paste: string) {
    const { data, error } = await apiClient.POST(
        "/pve/api/search/items/",
        { body: paste }
    );
    if (error) {
        throw error;
    }
    return data;
}

export async function getEntryItems(rotationId: number, entryId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/entries/{entry_id}/items/",
        { params: { path: { rotation_id: rotationId, entry_id: entryId } } }
    );
}

export async function getRotationItems(rotationId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/items/",
        { params: { path: { rotation_id: rotationId } } }
    );
}
