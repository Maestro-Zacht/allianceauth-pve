import { useTranslation } from "react-i18next";
import type { EntryFormErrors, ExtendedEntryFormSchema } from "../EntryTypes";
import "./RolesSectionStyles.css";
import { Alert, Button, Form } from "react-bootstrap";
import TooltipComponent from "../../utils/TooltipComponent";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import NewRoleForm from "./NewRoleForm";
import LoadRoleSetupsModal from "./LoadRoleSetupsModal";
import { Fragment, useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { getRotationRoleSetups } from "../../../api/api";
import Loading from "../../utils/Loading";

type RoleType = ExtendedEntryFormSchema["roles"][number];

function sameRoles(roles: RoleType[], setupRoles: RoleType[]) {
    const values = new Map(roles.map(role => [role.name, role.value]));
    return roles.length === setupRoles.length && setupRoles.every(role => values.get(role.name) === role.value);
}

interface RolesSectionProps {
    rotationId: number;
    roles: ExtendedEntryFormSchema["roles"];
    errors_root: EntryFormErrors["roles_root"] | null | undefined;
    errors: EntryFormErrors["roles"] | null | undefined;
}

export default function RolesSection({ rotationId, roles, errors_root, errors }: RolesSectionProps) {
    const { t } = useTranslation();
    const { updateEntryData } = useEntryProcessor();
    const { isLoading, data, error } = useQuery({
        queryKey: ["rotations", rotationId, "role_setups"],
        queryFn: () => getRotationRoleSetups(rotationId),
    });

    const lockedSetup = data?.lock_roles_setup ? data.roles_setups[0] : null;

    useEffect(() => {
        if (lockedSetup && !sameRoles(roles, lockedSetup.roles)) {
            updateEntryData({ type: 'load_role_setup', roles: lockedSetup.roles });
        }
    }, [lockedSetup, roles, updateEntryData]);

    if (isLoading) {
        return <div className="text-center"><Loading /></div>
    }

    if (error || !data) {
        return <div>Error loading role setups</div>
    }

    return <>
        <div id="roles-div" className={lockedSetup ? "text-center locked" : "text-center"}>
            <span>{t("role")}</span>
            <span>{t("value")}</span>
            {!lockedSetup && <span>{t("delete")}</span>}

            {roles.map((role, index) => <Fragment key={`role-${index}`}>
                <span className="text-truncate" title={role.name}>{role.name}</span>
                {lockedSetup ?
                    <span>{role.value}</span> :
                    <>
                        <Form.Control
                            value={role.value}
                            type="number"
                            onChange={(e) => {
                                const newValue = Number(e.target.value);
                                updateEntryData({ type: 'update_role_value', roleName: role.name, value: newValue });
                            }}
                        />
                        <TooltipComponent id={`delete-role-tooltip-${index}`} text={t("delete_role")}>
                            <Button
                                variant="danger"
                                style={{ transform: 'scale(0.75)' }}
                                onClick={() => updateEntryData({ type: 'delete_role', roleName: role.name })}
                                disabled={roles.length === 1}
                            >
                                <i className="fa-solid fa-trash-can"></i>
                            </Button>
                        </TooltipComponent>
                    </>}
                {errors && Object.keys(errors).length > 0
                    && errors[index] && Object.keys(errors[index]).length > 0
                    && <Alert variant="danger" className="all-cols" dismissible>
                        {errors[index].name.map((error, errorIndex) => <div key={`error-name-${index}-${errorIndex}`}>{error}</div>)}
                        {errors[index].value.map((error, errorIndex) => <div key={`error-value-${index}-${errorIndex}`}>{error}</div>)}
                    </Alert>}
            </Fragment>)}
        </div>
        {errors_root && errors_root.length > 0 && <Alert variant="danger" dismissible className="mt-3">
            {errors_root.map((error, index) => <div key={`error-root-${index}`}>{error}</div>)}
        </Alert>}
        {!lockedSetup && <div className="d-flex justify-content-evenly align-items-center">
            <NewRoleForm existingRoleNames={roles.map(r => r.name)} />
            <LoadRoleSetupsModal roleSetups={data.roles_setups} />
        </div>}
    </>
}
