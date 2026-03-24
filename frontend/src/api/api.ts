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
    const { data, error } = await apiClient.GET(url, fetchOptions);
    if (error) {
        console.error(`Error fetching ${String(url)}:`, error);
        throw error;
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
    return await genericGet("/pve/api/rolesetups/");
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