import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Row } from "react-bootstrap";
import { Navigate, useNavigate, useParams } from "react-router";
import { editEntry, getEntryEditData } from "../../../api/api";
import type { components } from "../../../api/Schema";
import { useToast } from "../../../providers/ToastProvider";
import { useTranslation } from "react-i18next";
import Loading from "../../Loading";
import type { EntryFormErrors, EntryFormSchema, ExtendedEntryFormSchema } from "../EntryTypes";
import { useState } from "react";
import { EntryFormProvider } from "../../../providers/EntryFormProvider";
import EntryForm from "./EntryForm";
import NavBackButton from "../../NavBackButton";

export default function EditEntryForm() {
    const [formErrors, setFormErrors] = useState<EntryFormErrors | null>(null);
    const { t } = useTranslation();
    const { rotationId, entryId } = useParams();
    const rotationIdNum = Number(rotationId);
    const entryIdNum = Number(entryId);
    const { isLoading, error, data } = useQuery<components["schemas"]["ExtendedEntryFormSchema"], string | number>({
        queryKey: ['rotation', rotationIdNum, 'entry', entryIdNum, 'edit_data'],
        queryFn: () => getEntryEditData(rotationIdNum, entryIdNum),
    });
    const queryClient = useQueryClient();
    const addToast = useToast();
    const navigate = useNavigate();
    const mutation = useMutation({
        mutationFn: (data: EntryFormSchema) => editEntry(rotationIdNum, entryIdNum, data),
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['rotation', rotationIdNum] });
            addToast(t('entry_changed'));
            navigate(`/pve/r/rotations/${rotationIdNum}/entries/${entryIdNum}/`);
        },
        onError: (error: number | string | EntryFormErrors) => {
            if (typeof error === "number") {
                addToast(t('entry_failed_code', { error }), 'danger');
            } else if (typeof error === "string") {
                addToast(t('entry_failed', { error }), 'danger');
            } else {
                setFormErrors(error);
                addToast(t('entry_change_failed'), 'danger');
            }
        }
    });

    if (error) {
        if (typeof error === 'string') {
            addToast(error, 'danger');
        } else {
            addToast(t("error", { code: error }), 'danger');
        }
        return <Navigate to={`/pve/r/`} />;
    }

    if (isLoading) {
        return <div className="text-center"><Loading /></div>;
    }

    const entryInitialData: ExtendedEntryFormSchema = {
        ...data!,
        shares: data!.shares.map(share => ({
            ...share,
            is_present: true,
        }))
    };

    const submitEntry = (entryFormData: ExtendedEntryFormSchema) => {
        const sendData: EntryFormSchema = {
            estimated_total: entryFormData.estimated_total,
            funding_percentage: entryFormData.funding_percentage,
            funding_project_id: entryFormData.funding_project_id,
            shares: entryFormData.shares.map(share => ({
                character_id: share.character_id,
                helped_setup: share.helped_setup,
                role_name: share.role_name,
                site_count: share.site_count,
            })),
            roles: entryFormData.roles,
            items: entryFormData.items.map(item => ({
                id: item.id,
                quantity: item.quantity,
            })),
        };
        mutation.mutate(sendData);
        setFormErrors(null);
    }

    return <>
        <NavBackButton url={`/pve/r/rotations/${rotationIdNum}/entries/${entryIdNum}/`} />
        <Row>
            <EntryFormProvider initialData={entryInitialData} submitEntry={submitEntry}>
                <EntryForm rotationId={rotationIdNum} isLoading={mutation.isPending} errors={formErrors} />
            </EntryFormProvider>
        </Row>
    </>
}
