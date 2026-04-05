import { Container, Row } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import type { ExtendedEntryFormSchema } from "./EntryTypes";
import { useNavigate, useParams } from "react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createEntry } from "../../api/api";
import { useToast } from "../../providers/ToastProvider";
import { EntryFormProvider } from "../../providers/EntryFormProvider";
import EntryForm from "./entry_form/EntryForm";



export default function NewEntryForm() {
    const { rotationId } = useParams();
    const rotationIdNum = Number(rotationId);
    const { t } = useTranslation();
    const queryClient = useQueryClient();
    const addToast = useToast();
    const navigate = useNavigate();
    const mutation = useMutation({
        mutationFn: (data: ExtendedEntryFormSchema) => createEntry(rotationIdNum, data),
        onSuccess: async () => {
            await queryClient.invalidateQueries({ queryKey: ['rotation', rotationIdNum] });
            addToast(t('entry_created'));
            navigate(`/pve/r/rotations/${rotationIdNum}/`);
        }
    });

    const submitEntry = (entryFormData: ExtendedEntryFormSchema) => {
        // mutation.mutate(entryFormData);
        alert(JSON.stringify(entryFormData, null, 2));
        mutation;
    }

    const initialEntryData: ExtendedEntryFormSchema = {
        estimated_total: 0,
        funding_percentage: null,
        funding_project_id: null,
        shares: [],
        roles: [{ name: 'Krab', value: 1 }],
    };

    return <>
        <Container fluid>
            <Row>
                <EntryFormProvider initialData={initialEntryData} submitEntry={submitEntry}>
                    <EntryForm rotationId={rotationIdNum} />
                </EntryFormProvider>
            </Row>
        </Container>
    </>
}
