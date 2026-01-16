import apiClient from "./ApiClient";
import type { paths } from "./Schema";
import type { FetchOptions } from "openapi-fetch";

export async function getUserPastActivity(months: number) {
    const { data, error } = await apiClient.GET(
        "/pve/api/activity/months/{months}/",
        { params: { path: { months } } }
    );
    if (error) {
        console.error("Error fetching user past activity:", error);
        throw error;
    }
    return data;
}

export async function getRotationList() {
    const { data, error } = await apiClient.GET("/pve/api/rotations/");
    if (error) {
        console.error("Error fetching rotation list:", error);
        throw error;
    }
    return data;
}

export async function getRotation(rotationId: number) {
    const { data, error } = await apiClient.GET(
        "/pve/api/rotations/{rotation_id}/",
        { params: { path: { rotation_id: rotationId } } }
    );
    if (error) {
        console.error("Error fetching rotation:", error);
        throw error;
    }
    return data;
}

export async function getProjectList() {
    const { data, error } = await apiClient.GET("/pve/api/projects/");
    if (error) {
        console.error("Error fetching project list:", error);
        throw error;
    }
    return data;
}

export async function getRotationSummary(rotationId: number) {
    const { data, error } = await apiClient.GET(
        "/pve/api/rotations/{rotation_id}/summary/",
        { params: { path: { rotation_id: rotationId } } }
    );
    if (error) {
        console.error("Error fetching rotation summary:", error);
        throw error;
    }
    return data;
}

export async function getRotationProjectsSummaries(rotationId: number) {
    const { data, error } = await apiClient.GET(
        "/pve/api/rotations/{rotation_id}/project_summaries/",
        { params: { path: { rotation_id: rotationId } } }
    );
    if (error) {
        console.error("Error fetching rotation summary:", error);
        throw error;
    }
    return data;
}

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

export async function getRotationEntries(rotationId: number) {
    return await genericGet(
        "/pve/api/rotations/{rotation_id}/entries/",
        { params: { path: { rotation_id: rotationId } } }
    );
}