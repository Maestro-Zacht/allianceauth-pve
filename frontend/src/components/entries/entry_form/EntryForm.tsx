import { Button, Card, Col } from "react-bootstrap";
import SharesSection from "./SharesSection";
import RolesSection from "./RolesSection";
import { useEntryFormData, useEntryProcessor } from "../../../providers/EntryFormProvider";
import { useTranslation } from "react-i18next";

interface EntryFormProps {
    rotationId: number;
}

export default function EntryForm({ rotationId }: EntryFormProps) {
    const { t } = useTranslation();
    const entryData = useEntryFormData();
    const { submitEntry } = useEntryProcessor();

    return <>
        <Col xs={12} >
            <Card>
                <Card.Body>
                    <RolesSection rotationId={rotationId} roles={entryData.roles} />
                    <hr />
                    <SharesSection shares={entryData.shares} />
                    <div className="d-flex flex-row-reverse">
                        <Button onClick={submitEntry}>{t("submit")}</Button>
                    </div>
                </Card.Body>
            </Card>
        </Col>
    </>
}
