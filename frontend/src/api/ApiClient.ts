import type { paths } from "./Schema";
import Cookies from "js-cookie";
import createClient from "openapi-fetch";

const apiClient = createClient<paths>({
    baseUrl: "/",
    headers: {
        "X-CSRFToken": Cookies.get("csrftoken") || "",
    },
});

export default apiClient;
