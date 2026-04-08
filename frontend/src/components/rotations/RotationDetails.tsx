import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router";
import { getRotation } from "../../api/api";
import Loading from "../Loading";
import type { components } from "../../api/Schema";
import { CardGroup, Col, Row } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import TimeAgo from "react-timeago";
import RotationSummarySection from "./RotationSummarySection";
import RotationEntriesSection from "./RotationEntriesSection";
import { GroupCard } from "../StatCards";
import CloseRotationSection from "./CloseRotationSection";
import NavBackButton from "../NavBackButton";
import { usePermissions } from "../../providers/PermissionsProvider";

type rotationType = components["schemas"]["RotationSchema"];

interface RotationHeaderProps {
    rotation: rotationType;
}


function RotationHeader({ rotation }: RotationHeaderProps) {
    const { t, i18n } = useTranslation();
    const permissions = usePermissions();

    const localizedTaxRate = (rotation.tax_rate / 100).toLocaleString(
        i18n.language,
        { style: 'percent' }
    );

    return <>
        <h1 className="page-header text-center">{rotation.name}</h1>
        <Col xs={12} className="my-3">
            <CardGroup>
                {rotation.is_closed ?
                    <GroupCard
                        title={t("status")}
                        value={t("closed")}
                    />
                    :
                    <GroupCard
                        title={t("age")}
                        value={<TimeAgo date={rotation.created_at} />}
                    />
                }
                <GroupCard
                    title={t("estimated_total")}
                    value={rotation.estimated_total.toLocaleString(i18n.language)}
                />
                {rotation.is_closed && (
                    <GroupCard
                        title={t("actual_total")}
                        value={rotation.actual_total.toLocaleString(i18n.language)}
                    />
                )}
                <GroupCard
                    title={t("tax_rate")}
                    value={localizedTaxRate}
                />
                {!rotation.is_closed && permissions && permissions.manage_rotations && (
                    <GroupCard
                        title={t("actions")}
                        value={<>
                            <CloseRotationSection rotationId={rotation.id} />
                        </>}
                    />
                )}
            </CardGroup>
        </Col>
    </>
}

export default function RotationDetails() {
    const { rotationId } = useParams();
    const rotationIdNum = Number(rotationId);
    const { data, isLoading, error } = useQuery({
        queryKey: ['rotation', rotationIdNum],
        queryFn: () => getRotation(rotationIdNum),
    });

    if (error) {
        console.error("Error loading rotation data:", error);
        return <div>Error loading rotation data.</div>;
    }

    return <>
        <NavBackButton url={`/pve/r/`} />
        {isLoading ?
            <Row>
                <Col xs={12} className="text-center">
                    <Loading />
                </Col>
            </Row> :
            <Row>
                <RotationHeader rotation={data!} />
                <RotationSummarySection rotationId={data!.id} isClosed={data!.is_closed} />
                <RotationEntriesSection rotationId={data!.id} isClosed={data!.is_closed} />
            </Row>
        }
    </>
}
