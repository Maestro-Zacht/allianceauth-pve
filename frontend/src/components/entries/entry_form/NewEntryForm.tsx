import { Row } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import type { ExtendedEntryFormSchema, EntryFormSchema, EntryFormErrors } from "../EntryTypes";
import { useNavigate, useParams } from "react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createEntry } from "../../../api/api";
import { useToast } from "../../../providers/ToastProvider";
import { EntryFormProvider } from "../../../providers/EntryFormProvider";
import EntryForm from "./EntryForm";
import { useState } from "react";
import NavBackButton from "../../NavBackButton";



export default function NewEntryForm() {
    const [formErrors, setFormErrors] = useState<EntryFormErrors | null>(null);
    const { rotationId } = useParams();
    const rotationIdNum = Number(rotationId);
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const addToast = useToast();
    const navigate = useNavigate();
    const mutation = useMutation({
        mutationFn: (data: EntryFormSchema) => createEntry(rotationIdNum, data),
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['rotation', rotationIdNum] });
            addToast(t('entry_created'));
            navigate(`/pve/r/rotations/${rotationIdNum}/`);
        },
        onError: (error: number | string | EntryFormErrors) => {
            if (typeof error === "number") {
                addToast(t('entry_failed_code', { error }), 'danger');
            } else if (typeof error === "string") {
                addToast(t('entry_failed', { error }), 'danger');
            } else {
                setFormErrors(error);
                addToast(t('entry_creation_failed'), 'danger');
            }
        }
    });

    const submitEntry = (entryFormData: ExtendedEntryFormSchema, resetFunction: () => void) => {
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
        mutation.mutate(sendData, {
            onSuccess: () => {
                resetFunction();
            }
        });
        setFormErrors(null);
    }

    const initialEntryData: ExtendedEntryFormSchema = {
        estimated_total: 0,
        funding_percentage: null,
        funding_project_id: null,
        shares: [],
        roles: [{ name: 'Krab', value: 1 }],
        items: [],
    };

    return <>
        <NavBackButton url={`/pve/r/rotations/${rotationIdNum}/`} />
        <Row>
            <EntryFormProvider initialData={initialEntryData} localStorageKey={`new-entry-form-${rotationIdNum}`} submitEntry={submitEntry}>
                <EntryForm rotationId={rotationIdNum} isLoading={mutation.isPending} errors={formErrors} />
            </EntryFormProvider>
        </Row>
    </>
}
