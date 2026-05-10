import { Fragment } from "react";
import { useTranslation } from "react-i18next";
import type { EntryFormErrors, ExtendedEntryFormSchema } from "../EntryTypes";
import "./ShareSectionStyles.css";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import CharacterWithPortrait from "../../utils/CharacterWithPortrait";
import { Alert, Button, Form } from "react-bootstrap";

interface SharesSectionProps {
    shares: ExtendedEntryFormSchema['shares'];
    roles: ExtendedEntryFormSchema['roles'];
    errors_root: EntryFormErrors['shares_root'] | undefined | null;
    errors: EntryFormErrors['shares'] | undefined | null;
}

export default function SharesSection({ shares, roles, errors_root, errors }: SharesSectionProps) {
    const { t } = useTranslation();
    const { updateEntryData } = useEntryProcessor();

    return <>
        <div id="users">
            {shares.length === 0 ?
                <span className="all-cols text-center">{t("no_character_yet")}</span> :
                <>
                    <span className="text-center">{t("select")}</span>
                    <span>{t("users_main_character")}</span>
                    <span>{t("character")}</span>
                    <span className="text-center">{t("role")}</span>
                    <span className="text-center">{t("setup")}</span>
                    <span className="text-center">{t("count")}</span>
                    <span className="text-center">{t("delete")}</span>

                    {shares.map((share, index) => <Fragment key={index}>
                        <span
                            className="text-center align-self-center"
                            onClick={() => updateEntryData({
                                type: "toggle_share_value",
                                characterId: share.character_id,
                                field: "is_present"
                            })}
                        >
                            {share.is_present ?
                                <i className="fas fa-arrow-right selected-user"></i> :
                                <i className="fas fa-running unselected-user"></i>}
                        </span>
                        <span className="d-flex justify-content-start align-items-center">
                            <CharacterWithPortrait
                                character_name={share.main_character_name}
                                portrait_url={share.main_character_portrait_url}
                            />
                        </span>
                        <span className="d-flex justify-content-start align-items-center">
                            <CharacterWithPortrait
                                character_name={share.character_name}
                                portrait_url={share.portrait_url}
                            />
                        </span>
                        <Form.Select
                            value={share.role_name}
                            onChange={(e) => updateEntryData({
                                type: "change_share_role",
                                characterId: share.character_id,
                                newRoleName: e.target.value
                            })}
                        >
                            {roles.map((role) => <option key={role.name} value={role.name}>{role.name}</option>)}
                        </Form.Select>
                        <span
                            className="text-center align-self-center"
                            onClick={() => updateEntryData({
                                type: "toggle_share_value",
                                characterId: share.character_id,
                                field: "helped_setup"
                            })}
                        >
                            {share.helped_setup ?
                                <i className="fas fa-heart fa-heart-red"></i> :
                                <i className="far fa-heart fa-heart-red"></i>
                            }
                        </span>
                        <Form.Control
                            type="number"
                            min={0}
                            value={share.site_count}
                            onChange={(e) => updateEntryData({
                                type: "update_share_count",
                                characterId: share.character_id,
                                value: parseInt(e.target.value)
                            })}
                            style={{ maxWidth: "7ch" }}
                        />
                        <Button
                            variant="danger"
                            style={{ transform: 'scale(0.8)' }}
                            onClick={() => {
                                updateEntryData({
                                    type: 'delete_share',
                                    characterId: share.character_id
                                });
                            }}
                        >
                            <i className="fa-solid fa-trash-can"></i>
                        </Button>
                        {errors && Object.keys(errors).length > 0
                            && errors[index] && Object.keys(errors[index]).length > 0
                            && <Alert variant="danger" className="all-cols" dismissible>
                                {errors[index].role_name && errors[index].role_name.map((error, errorIndex) => <div key={`error-role-${index}-${errorIndex}`}>{error}</div>)}
                                {errors[index].site_count && errors[index].site_count.map((error, errorIndex) => <div key={`error-count-${index}-${errorIndex}`}>{error}</div>)}
                            </Alert>}
                    </Fragment>)}
                </>
            }
        </div>
        {errors_root && errors_root.length > 0 && <Alert variant="danger" className="mt-3" dismissible>
            {errors_root.map((error, index) => <div key={index}>{error}</div>)}
        </Alert>}
    </>
}
