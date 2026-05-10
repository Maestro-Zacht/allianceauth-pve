import { useQuery } from "@tanstack/react-query";
import { Card, Col, Table } from "react-bootstrap";
import { getEntryRoles } from "../../api/api";
import { useTranslation } from "react-i18next";
import Loading from "../utils/Loading";
import type { components } from "../../api/Schema";

type EntryRoleType = components["schemas"]["EntryRoleSchema"]

interface EntryRolesProps {
    rotationId: number;
    entryId: number;
}

interface RolesTableProps {
    roles: EntryRoleType[];
}

interface RoleRowProps {
    role: EntryRoleType;
}

function RoleRow({ role }: RoleRowProps) {
    const { i18n } = useTranslation();

    const localizePercentage = (num: number) => {
        return num.toLocaleString(i18n.language, {
            style: 'percent',
            minimumFractionDigits: 0,
            maximumFractionDigits: 1
        });
    }

    return <tr>
        <td>{role.name}</td>
        <td>{role.value}</td>
        <td>{localizePercentage(role.role_approximate_percentage / 100)}</td>
    </tr>;
}

function RolesTable({ roles }: RolesTableProps) {
    const { t } = useTranslation();
    return <>
        <Table className="table-aa">
            <thead>
                <tr>
                    <th scope="col">{t('role')}</th>
                    <th scope="col">{t('value')}</th>
                    <th scope="col">{t('approximate_percentage')}</th>
                </tr>
            </thead>
            <tbody>
                {roles.map((role, index) => (
                    <RoleRow key={index} role={role} />
                ))}
            </tbody>
        </Table>
    </>
}

export default function EntryRoles({ rotationId, entryId }: EntryRolesProps) {
    const { t } = useTranslation();
    const { data, error, isLoading } = useQuery({
        queryKey: [rotationId, entryId, "roles"],
        queryFn: () => getEntryRoles(rotationId, entryId),
    });

    if (error) {
        console.error("Error loading entry roles:", error);
        return <div>Error loading entry roles.</div>;
    }

    const roles = data || [];

    return <>
        <Col xs={12} className="my-3">
            <Card className="text-center">
                <Card.Header>{t("fleet_role", { count: roles.length })}</Card.Header>
                <Card.Body>
                    {isLoading ? <Loading /> : <RolesTable roles={roles} />}
                </Card.Body>
            </Card>
        </Col>
    </>
}
