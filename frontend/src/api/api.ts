import apiClient from "./ApiClient";

export async function getUserPastActivity(months: number) {
    const { data, error } = await apiClient.GET(
        "/pve/api/activity/months/{months}",
        { params: { path: { months } } }
    );
    if (error) {
        console.error("Error fetching user past activity:", error);
        throw error;
    }
    return data;
}

export async function getRotationList() {
    const { data, error } = await apiClient.GET("/pve/api/rotations/rotations");
    if (error) {
        console.error("Error fetching rotation list:", error);
        throw error;
    }
    return data;
}

export async function getProjectList() {
    const { data, error } = await apiClient.GET("/pve/api/projects/projects");
    if (error) {
        console.error("Error fetching project list:", error);
        throw error;
    }
    return data;
}
