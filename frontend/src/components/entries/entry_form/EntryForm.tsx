import { Button, Card, Col, Row } from "react-bootstrap";
import SharesSection from "./SharesSection";
import RolesSection from "./RolesSection";
import { useEntryFormData, useEntryProcessor } from "../../../providers/EntryFormProvider";
import { useTranslation } from "react-i18next";
import IncrementTotalSection from "./IncrementTotalSection";
import TotalSection from "./TotalSection";
import AddCharactersSection from "./AddCharactersSection";
import FundingProjectSection from "./FundingProjectSection";
import SiteScalingSection from "./SiteScalingSection";
import "./EntryFormStyles.css"
import Loading from "../../utils/Loading";
import type { EntryFormErrors } from "../EntryTypes";

interface EntryFormProps {
    rotationId: number;
    isLoading: boolean;
    errors: EntryFormErrors | null;
}

export default function EntryForm({ rotationId, isLoading, errors }: EntryFormProps) {
    const { t } = useTranslation();
    const entryData = useEntryFormData();
    const { submitEntry } = useEntryProcessor();

    return <>
        <Col xs={12} sm={8}>
            <Card>
                <Card.Body>
                    <Row>
                        <Col lg>
                            <RolesSection rotationId={rotationId} roles={entryData.roles} errors_root={errors?.roles_root} errors={errors?.roles} />
                        </Col>
                        <Col lg="auto" className="d-none d-lg-flex">
                            <div className="vr" />
                        </Col>
                        <Col lg={4}>
                            <hr className="d-lg-none" />
                            <SiteScalingSection
                                siteScaling={entryData.site_scaling}
                                siteScalingCoefficient={entryData.site_scaling_coefficient ?? null}
                                errorsSiteScalingCoefficient={errors?.site_scaling_coefficient}
                            />
                        </Col>
                    </Row>
                    <hr />
                    <IncrementTotalSection rotationId={rotationId} />
                    <hr />
                    <TotalSection estimatedTotal={entryData.estimated_total} errors={errors?.estimated_total} items={entryData.items} />
                    <hr />
                    <SharesSection shares={entryData.shares} roles={entryData.roles} errors_root={errors?.shares_root} errors={errors?.shares} />
                    <FundingProjectSection
                        fundingProjectId={entryData.funding_project_id}
                        fundingPercentage={entryData.funding_percentage}
                        errorsFundingProjectId={errors?.funding_project_id}
                        errorsFundingPercentage={errors?.funding_percentage}
                    />
                    <div className="d-flex flex-row-reverse mt-3">
                        <Button onClick={submitEntry} disabled={isLoading}>
                            {isLoading ? <Loading size="sm" /> : t("submit")}
                        </Button>
                    </div>
                </Card.Body>
            </Card>
        </Col>
        <Col xs={12} sm={4}>
            <Card>
                <Card.Body>
                    <AddCharactersSection addedCharacterIds={entryData.shares.map((share) => share.character_id)} />
                </Card.Body>
            </Card>
        </Col>
    </>
}
