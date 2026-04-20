import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router";
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
import TooltipComponent from "../TooltipComponent";

type rotationType = components["schemas"]["RotationSchema"];

interface RotationHeaderProps {
    rotation: rotationType;
}


function RotationHeader({ rotation }: RotationHeaderProps) {
    const { t, i18n } = useTranslation();
    const permissions = usePermissions();

    const localizePercentage = (num: number) => {
        return num.toLocaleString(i18n.language, {
            style: 'percent',
        });
    }

    return <>
        <h1 className="page-header text-center">{rotation.name}</h1>
        <Col xs={12} className="my-3">
            <CardGroup>
                {rotation.is_closed ?
                    <GroupCard
                        title={t("status")}
                        value={t("closed")}
                        align
                    />
                    :
                    <GroupCard
                        title={t("age")}
                        value={<TimeAgo date={rotation.created_at} />}
                        align
                    />
                }
                <GroupCard
                    title={t("estimated_total")}
                    value={t("isk", { isk: rotation.estimated_total })}
                    align
                />
                {rotation.is_closed && (
                    <GroupCard
                        title={t("actual_total")}
                        value={
                            <TooltipComponent id="actual-total-tooltip" text={t("total_from_items_tooltip", { total: rotation.actual_total, items: rotation.actual_total_from_items })}>
                                <span>{t("isk", { isk: rotation.actual_total + rotation.actual_total_from_items })}</span>
                            </TooltipComponent>
                        }
                        align
                    />
                )}
                <GroupCard
                    title={t("tax_rate")}
                    value={<>
                        {localizePercentage(rotation.tax_rate / 100)} / {localizePercentage(rotation.tax_rate_loot_items / 100)} ({t("items")})
                    </>}
                    align
                />
                {!rotation.is_closed && permissions && (permissions.manage_rotations || permissions.manage_entries) && (
                    <GroupCard
                        title={t("actions")}
                        value={<>
                            {permissions.manage_rotations && <CloseRotationSection rotationId={rotation.id} />}
                            {permissions.manage_entries && (
                                <TooltipComponent id="add-entry-tooltip" text={t("new_entry")}>
                                    <Link to={`/pve/r/rotations/${rotation.id}/entries/new/`} className="btn btn-success ms-3">
                                        <i className="fa-solid fa-plus"></i>
                                    </Link>
                                </TooltipComponent>
                            )}
                        </>}
                        align
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
                <RotationEntriesSection rotationId={data!.id} isRotationClosed={data!.is_closed} />
            </Row>
        }
    </>
}
