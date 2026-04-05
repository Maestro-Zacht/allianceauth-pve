import { useTranslation } from "react-i18next";
import type { ExtendedEntryFormSchema } from "../EntryTypes";
import "./EntryFormStyles.css"
import { Button, Form } from "react-bootstrap";
import TooltipComponent from "../../TooltipComponent";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import NewRoleForm from "./NewRoleForm";
import LoadRoleSetupsModal from "./LoadRoleSetupsModal";


interface RolesSectionProps {
    rotationId: number;
    roles: ExtendedEntryFormSchema["roles"];
}

export default function RolesSection({ rotationId, roles }: RolesSectionProps) {
    const { t } = useTranslation();
    const { updateEntryData } = useEntryProcessor();

    return <>
        <div id="roles-div" className="text-center">
            <span>{t("role")}</span>
            <span>{t("value")}</span>
            <span>{t("delete")}</span>

            {roles.map((role, index) => <>
                <span key={`role-name-${index}`}>{role.name}</span>
                <Form.Control
                    key={`role-value-${index}`}
                    value={role.value}
                    type="number"
                    onChange={(e) => {
                        const newValue = Number(e.target.value);
                        updateEntryData({ type: 'update_role_value', roleName: role.name, value: newValue });
                    }}
                />
                <TooltipComponent key={`delete-role-tooltip-${index}`} id={`delete-role-tooltip-${index}`} text={t("delete_role")}>
                    <Button
                        key={`role-delete-${index}`}
                        variant="danger"
                        style={{ transform: 'scale(0.75)' }}
                        onClick={() => updateEntryData({ type: 'delete_role', roleName: role.name })}
                        disabled={roles.length === 1}
                    >
                        <i className="fa-solid fa-trash-can"></i>
                    </Button>
                </TooltipComponent>
            </>)}
        </div>
        <div className="d-flex justify-content-evenly align-items-center">
            <NewRoleForm existingRoleNames={roles.map(r => r.name)} />
            <LoadRoleSetupsModal rotationId={rotationId} />
        </div>
    </>
}
