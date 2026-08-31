import { Button, Card, Col, Form, ToggleButton, ToggleButtonGroup } from "react-bootstrap";
import SharesSection from "./SharesSection";
import RolesSection from "./RolesSection";
import { useEntryFormData, useEntryProcessor } from "../../../providers/EntryFormProvider";
import type { EntryMode, RampancyLevel } from "../EntryTypes";
import { RAMPANCY_LEVELS } from "./waveShares";
import { useTranslation } from "react-i18next";
import IncrementTotalSection from "./IncrementTotalSection";
import TotalSection from "./TotalSection";
import AddCharactersSection from "./AddCharactersSection";
import FundingProjectSection from "./FundingProjectSection";
import "./EntryFormStyles.css"
import Loading from "../../utils/Loading";
import type { EntryFormErrors } from "../EntryTypes";

interface EntryFormProps {
    rotationId: number;
    isLoading: boolean;
    errors: EntryFormErrors | null;
}

const RAMPANCY_LABEL_KEY = {
    minimal: "rampancy_minimal",
    moderate: "rampancy_moderate",
    severe: "rampancy_severe",
    critical: "rampancy_critical",
} as const satisfies Record<RampancyLevel, string>;

export default function EntryForm({ rotationId, isLoading, errors }: EntryFormProps) {
    const { t } = useTranslation();
    const entryData = useEntryFormData();
    const { submitEntry, updateEntryData } = useEntryProcessor();

    return <>
        <Col xs={12} sm={8}>
            <Card>
                <Card.Body>
                    <div className="d-flex justify-content-center mb-3">
                        <ToggleButtonGroup
                            type="radio"
                            name="entry-mode"
                            value={entryData.mode}
                            onChange={(mode: EntryMode) => updateEntryData({ type: 'set_mode', mode })}
                        >
                            <ToggleButton id="entry-mode-sites" value="sites" variant="outline-primary">
                                {t("mode_sites")}
                            </ToggleButton>
                            <ToggleButton id="entry-mode-fabs" value="fabs" variant="outline-primary">
                                {t("mode_fabs")}
                            </ToggleButton>
                        </ToggleButtonGroup>
                    </div>
                    {entryData.mode === 'fabs' && <Form.Group controlId="rampancy-level" className="d-flex justify-content-center align-items-center gap-2 mb-3">
                        <Form.Label className="mb-0">{t("rampancy_level")}</Form.Label>
                        <Form.Select
                            style={{ maxWidth: "12rem" }}
                            value={entryData.rampancy_level}
                            onChange={(e) => updateEntryData({ type: 'set_rampancy_level', level: e.target.value as RampancyLevel })}
                        >
                            {RAMPANCY_LEVELS.map((level) => (
                                <option key={level} value={level}>{t(RAMPANCY_LABEL_KEY[level])}</option>
                            ))}
                        </Form.Select>
                    </Form.Group>}
                    <RolesSection rotationId={rotationId} roles={entryData.roles} errors_root={errors?.roles_root} errors={errors?.roles} />
                    <hr />
                    <IncrementTotalSection rotationId={rotationId} />
                    <hr />
                    <TotalSection estimatedTotal={entryData.estimated_total} errors={errors?.estimated_total} items={entryData.items} mode={entryData.mode} />
                    <hr />
                    <SharesSection shares={entryData.shares} roles={entryData.roles} errors_root={errors?.shares_root} errors={errors?.shares} mode={entryData.mode} />
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
