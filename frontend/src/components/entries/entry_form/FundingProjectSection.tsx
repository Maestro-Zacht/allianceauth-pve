import { useQuery } from "@tanstack/react-query"
import { getActiveProjects } from "../../../api/api";
import Loading from "../../utils/Loading";
import { t } from "i18next";
import { Alert, Col, Form, Row } from "react-bootstrap";
import TooltipComponent from "../../utils/TooltipComponent";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";

interface FundingProjectSectionProps {
    fundingProjectId: number | null;
    fundingPercentage: number | null;
    errorsFundingProjectId: string[] | null | undefined;
    errorsFundingPercentage: string[] | null | undefined;
}

export default function FundingProjectSection({ fundingProjectId, fundingPercentage, errorsFundingProjectId, errorsFundingPercentage }: FundingProjectSectionProps) {
    const { updateEntryData } = useEntryProcessor();
    const { isLoading, error, data } = useQuery({
        queryKey: ["projects", "active"],
        queryFn: getActiveProjects
    });

    if (error) {
        return <div>Error loading projects</div>
    }

    const projects = data || [];

    return <>
        {isLoading ?
            <><hr /><div className="text-center"><Loading /></div></> :
            projects.length > 0 && <>
                <hr />
                <div className="text-center">
                    <h5>{t("funding_project_contribution")}</h5>
                </div>
                <Row className="justify-content-around align-items-center my-3">
                    <Col xs={6}>
                        <Form.Select
                            value={fundingProjectId || ""}
                            onChange={(e) => {
                                const projectId = e.target.value === "" ? null : parseInt(e.target.value);
                                updateEntryData({ type: 'select_funding_project', projectId });
                            }}
                        >
                            <option></option>
                            {projects.map(project => <option key={project.id} value={project.id}>{project.name}</option>)}
                        </Form.Select>
                        {errorsFundingProjectId && errorsFundingProjectId.length > 0 && <Alert variant="danger" className="mt-2" dismissible>
                            {errorsFundingProjectId.map((error, index) => <div key={index}>{error}</div>)}
                        </Alert>}
                    </Col>
                    <Col xs='auto'>
                        <Form.Group className="d-flex align-items-center gap-3">
                            <Form.Label>{t("percentage")}</Form.Label>
                            <TooltipComponent id="funding-percentage-tooltip" text={t("funding_percentage_tooltip")}>
                                <Form.Control
                                    type="number" min={1} max={100}
                                    value={fundingPercentage || ""}
                                    onChange={(e) => {
                                        const percentage = e.target.value === "" ? null : parseInt(e.target.value);
                                        if (percentage !== null) {
                                            updateEntryData({ type: 'update_funding_percentage', percentage });
                                        }
                                    }}
                                />
                            </TooltipComponent>
                        </Form.Group>
                        {errorsFundingPercentage && errorsFundingPercentage.length > 0 && <Alert variant="danger" className="mt-2" dismissible>
                            {errorsFundingPercentage.map((error, index) => <div key={index}>{error}</div>)}
                        </Alert>}
                    </Col>
                </Row>
            </>
        }
    </>
}
