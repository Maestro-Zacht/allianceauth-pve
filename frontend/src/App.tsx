import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { Navigate, Route, BrowserRouter as Router, Routes } from "react-router";

import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import Backend from "i18next-http-backend";
import LanguageDetector from "i18next-browser-languagedetector";

import ErrorPage from "./components/utils/ErrorPage";
import Dashboard from "./components/dashboard/Dashboard";
import RotationDetails from "./components/rotations/RotationDetails";
import { ToastProvider } from "./providers/ToastProvider";
import EntryDetails from "./components/entries/EntryDetails";
import ProjectDetails from "./components/projects/ProjectDetails";
import NewRotationForm from "./components/rotations/NewRotationForm";
import { PermissionsProvider } from "./providers/PermissionsProvider";
import NewProjectForm from "./components/projects/NewProjectForm";
import NewEntryForm from "./components/entries/entry_form/NewEntryForm";
import EditEntryForm from "./components/entries/entry_form/EditEntryForm";


const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false,
        }
    }
});

i18n
    .use(Backend)
    .use(initReactI18next)
    .use(LanguageDetector)
    .init({
        detection: {
            order: [
                "htmlTag",
                "querystring",
                "cookie",
                "localStorage",
                "sessionStorage",
                "navigator",
                "path",
                "subdomain",
            ],
            htmlTag: document.getElementById("root"),
        },
        fallbackLng: "en",
        interpolation: {
            escapeValue: false, // react already safes from xss => https://www.i18next.com/translation-function/interpolation#unescape
        },
        react: {
            useSuspense: false, //   <---- this will do the magic
        },
        backend: {
            loadPath: "/static/allianceauth_pve/react/i18n/{{lng}}/{{ns}}.json",
        },
    });

declare global {
    interface Window {
        __TANSTACK_QUERY_CLIENT__:
        import("@tanstack/query-core").QueryClient;
    }
}

if (import.meta.env.MODE === 'development') {
    window.__TANSTACK_QUERY_CLIENT__ = queryClient;
}

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <ToastProvider>
                <PermissionsProvider>
                    <Router>
                        <Routes>
                            <Route path="/pve/r/">
                                <Route index element={<Dashboard />} />
                                <Route path="rotations/">
                                    <Route path="new/" element={<NewRotationForm />} />
                                    <Route path=":rotationId/">
                                        <Route index element={<RotationDetails />} />
                                        <Route path="entries/">
                                            <Route path="new/" element={<NewEntryForm />} />
                                            <Route path=":entryId/">
                                                <Route index element={<EntryDetails />} />
                                                <Route path="edit/" element={<EditEntryForm />} />
                                            </Route>
                                        </Route>
                                    </Route>
                                </Route>
                                <Route path="projects/">
                                    <Route path="new/" element={<NewProjectForm />} />
                                    <Route path=":projectId/" element={<ProjectDetails />} />
                                </Route>
                                <Route path="*" element={<ErrorPage errorCode={404} message="Page Not Found" />} />
                            </Route>
                            <Route path="*" element={<Navigate to="/pve/r/" replace />} />
                        </Routes>
                    </Router>
                </PermissionsProvider>
            </ToastProvider>
        </QueryClientProvider>
    )
}

export default App
