import apiClient from "./ApiClient";
import type { paths } from "./Schema";
import type { FetchOptions } from "openapi-fetch";


async function genericGet<Path extends keyof paths>(
    url: Path,
    ...options: paths[Path] extends { get: any }
        ? [FetchOptions<paths[Path]["get"]>]
        : [never]
) {
    const [fetchOptions] = options;
    const { data, error } = await apiClient.GET(url, fetchOptions);
    if (error) {
        console.error(`Error fetching ${String(url)}:`, error);
        throw error;
    }
    return data as NonNullable<typeof data>;
}

export async function getUserPastActivity(months: number) {
    return await genericGet(
        "/pve/api/activity/months/{months}/",
        { params: { path: { months } } }
    );
}

export async function getRotationList() {
    return await genericGet("/pve/api/rotations/", {});
}

export async function getRotation(rotationId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/",
        { params: { path: { rotation_id: rotationId } } }
    );
}

export async function getProjectList() {
    return await genericGet("/pve/api/projects/", {});
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
