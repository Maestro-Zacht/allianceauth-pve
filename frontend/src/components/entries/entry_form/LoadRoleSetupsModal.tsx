import { Fragment, useState } from "react";
import { Button, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import type { components } from "../../../api/Schema";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";

interface LoadRoleSetupsModalProps {
    roleSetups: components["schemas"]["RoleSetupSchema"][];
}

export default function LoadRoleSetupsModal({ roleSetups }: LoadRoleSetupsModalProps) {
    const { t } = useTranslation();
    const [show, setShow] = useState(false);
    const { updateEntryData } = useEntryProcessor();

    return <>
        {roleSetups.length > 0 && <>
            <Button variant="success" onClick={() => setShow(true)}>
                {t("load_role_setups")}
            </Button>
            <Modal
                show={show}
                onHide={() => setShow(false)}
                backdrop="static"
            >
                <Modal.Header closeButton>
                    <Modal.Title>{t("load_role_setups")}</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    {roleSetups.map((setup, idx, array) => <Fragment key={`role-setup-${setup.id}`}>
                        <div className="mb-4">
                            <h5>{setup.name}</h5>
                            <small>
                                {setup.roles.map(role => `${role.name} (${role.value})`).join(", ")}
                            </small>
                        </div>
                        <Button
                            variant="success"
                            onClick={() => {
                                updateEntryData({
                                    type: 'load_role_setup',
                                    roles: setup.roles
                                })
                                setShow(false);
                            }}
                        >
                            {t("load")}
                        </Button>
                        {idx < array.length - 1 && <hr />}
                    </Fragment>)}
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="danger" onClick={() => setShow(false)}>
                        {t("cancel")}
                    </Button>
                </Modal.Footer>
            </Modal>
        </>}
    </>
}
