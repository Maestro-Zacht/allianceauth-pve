import { Card, CardGroup, Col, ProgressBar } from "react-bootstrap";
import type { components } from "../../api/Schema";
import { GroupCard } from "../StatCards";
import { useTranslation } from "react-i18next";
import TimeAgo from "react-timeago";

type ProjectType = components["schemas"]["FundingProjectSchema"];

interface ProjectInfoProps {
    project: ProjectType;
}

export default function ProjectInfo({ project }: ProjectInfoProps) {
    const { t, i18n } = useTranslation();

    const startDate = new Date(project.created_at);
    const completedDate = project.completed_at && new Date(project.completed_at);
    const completedInDays = completedDate && Math.round((completedDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24));

    const actualPercentage = (project.current_total / project.goal) * 100;
    const estimatedMissingPercentage = project.actual_percentage + project.estimated_missing_percentage <= 100
        ? project.estimated_missing_percentage
        : 100 - actualPercentage;
    const totalPercentage = actualPercentage + project.estimated_missing_percentage;

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language, {
            maximumFractionDigits: 0
        });
    }

    const localizePercentage = (num: number) => {
        return num.toLocaleString(i18n.language, {
            style: "percent",
            maximumFractionDigits: 2
        });
    }

    return <>
        <Col xs={12} className="mt-4">
            <CardGroup>
                <GroupCard
                    title={t("started")}
                    value={<TimeAgo date={project.created_at} />}
                    align={true}
                />
                {!project.is_active && <GroupCard
                    title={t("completed")}
                    value={<>
                        <TimeAgo date={project.completed_at!} />
                        <Card.Text>{t("completed_after_days", { days: completedInDays! })}</Card.Text>
                    </>}
                    align={true}
                />}
                <GroupCard
                    title={t("users")}
                    value={project.number_of_participants}
                    align={true}
                />
                {project.is_active && <GroupCard
                    title={t("estimated_total")}
                    value={localizeNumber(project.estimated_total)}
                    align={true}
                />}
                <GroupCard
                    title={t("current_total")}
                    value={localizeNumber(project.current_total)}
                    align={true}
                />
                <GroupCard
                    title={t("goal")}
                    value={localizeNumber(project.goal)}
                    align={true}
                />
            </CardGroup>
        </Col>
        <Col xs={12} className="mt-4">
            <ProgressBar style={{ height: "20px" }}>
                <ProgressBar
                    now={actualPercentage} min={0} max={100}
                    animated={project.is_active}
                    variant={actualPercentage >= 100 ? "success" : actualPercentage <= 1 ? "danger" : actualPercentage <= 25 ? "warning" : "info"}
                    label={localizePercentage(actualPercentage / 100)}
                    aria-label={t("actual_progress")}
                />
                {project.is_active && actualPercentage < 100 && <ProgressBar
                    now={estimatedMissingPercentage} min={0} max={100}
                    animated
                    variant={totalPercentage >= 100 ? "success" : undefined}
                    label={localizePercentage(project.estimated_missing_percentage / 100)}
                    aria-label={t("estimated_progress")}
                />}
            </ProgressBar>
        </Col>
    </>
}
