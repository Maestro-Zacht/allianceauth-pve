import { Button, Card, Col } from "react-bootstrap";
import SharesSection from "./SharesSection";
import RolesSection from "./RolesSection";
import { useEntryFormData, useEntryProcessor } from "../../../providers/EntryFormProvider";
import { useTranslation } from "react-i18next";
import IncrementTotalSection from "./IncrementTotalSection";
import TotalSection from "./TotalSection";
import AddCharactersSection from "./AddCharactersSection";
import FundingProjectSection from "./FundingProjectSection";

interface EntryFormProps {
    rotationId: number;
}

export default function EntryForm({ rotationId }: EntryFormProps) {
    const { t } = useTranslation();
    const entryData = useEntryFormData();
    const { submitEntry } = useEntryProcessor();

    return <>
        <Col xs={12} sm={8}>
            <Card>
                <Card.Body>
                    <RolesSection rotationId={rotationId} roles={entryData.roles} />
                    <hr />
                    <IncrementTotalSection rotationId={rotationId} />
                    <hr />
                    <TotalSection estimatedTotal={entryData.estimated_total} />
                    <hr />
                    <SharesSection shares={entryData.shares} />
                    <FundingProjectSection
                        fundingProjectId={entryData.funding_project_id}
                        fundingPercentage={entryData.funding_percentage}
                    />
                    <div className="d-flex flex-row-reverse">
                        <Button onClick={submitEntry}>{t("submit")}</Button>
                    </div>
                </Card.Body>
            </Card>
        </Col>
        <Col xs={12} sm={4}>
            <Card>
                <Card.Body>
                    <AddCharactersSection />
                </Card.Body>
            </Card>
        </Col>
    </>
}
