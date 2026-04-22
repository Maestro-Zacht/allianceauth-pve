import { Button, CardGroup, Col, Modal } from "react-bootstrap";
import { GroupCard } from "../StatCards";
import { useTranslation } from "react-i18next";
import TimeAgo from "react-timeago";
import CharacterWithPortrait from "../CharacterWithPortrait";
import type { components } from "../../api/Schema";
import TooltipComponent from "../TooltipComponent";
import { useState } from "react";
import { useToast } from "../../providers/ToastProvider";
import { Link, useNavigate } from "react-router";
import Loading from "../Loading";
import { deleteEntry } from "../../api/api";

type EntryType = components["schemas"]["EntryDetailsSchema"];

interface EntryInfoProps {
    entry: EntryType;
    rotationId: number;
}

export default function EntryInfo({ entry, rotationId }: EntryInfoProps) {
    const { t, i18n } = useTranslation();
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [deleting, setDeleting] = useState(false);
    const navigate = useNavigate();
    const addToast = useToast();

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language, {
            maximumFractionDigits: 0
        });
    }

    const handleDelete = async () => {
        setDeleting(true);
        try {
            await deleteEntry(rotationId, entry.id);
            navigate(`/pve/r/rotations/${rotationId}/`);
        } catch (error) {
            addToast(error as string, "danger");
        }
        finally {
            setDeleting(false);
            setShowDeleteConfirm(false);
        }
    }

    const total = entry.rotation_is_closed ?
        entry.actual_total_after_tax + entry.actual_total_from_items :
        entry.estimated_total;

    return <>
        <Col xs={12} className="my-3">
            <CardGroup>
                <GroupCard
                    title={t('created')}
                    value={<TimeAgo date={entry.created_at} />}
                />
                <GroupCard
                    title={t('number_of_users')}
                    value={entry.total_user_count}
                />
                {entry.funding_project && (
                    <GroupCard
                        title={t('funding_project')}
                        value={`${entry.funding_project.name} (${entry.funding_percentage}%)`}
                    />
                )}
                {!entry.rotation_is_closed && <GroupCard
                    title={t('total_after_tax')}
                    value={localizeNumber(entry.estimated_total_after_tax)}
                />}
                <GroupCard
                    title={t('total')}
                    value={entry.rotation_is_closed ?
                        <TooltipComponent
                            id={`total-${entry.id}-tooltip`}
                            text={t('total_from_items_tooltip', { total: entry.actual_total_after_tax, items: entry.actual_total_from_items })}
                        >
                            <span>{localizeNumber(total)}</span>
                        </TooltipComponent> :
                        localizeNumber(total)
                    }
                />
                <GroupCard
                    title={t('created_by')}
                    value={entry.created_by_character ? <CharacterWithPortrait
                        character_name={entry.created_by_character.character_name}
                        portrait_url={entry.created_by_character.portrait_url}
                    /> : t("missing_character")}
                />
                {entry.user_can_edit && !entry.rotation_is_closed && (
                    <GroupCard
                        title={t('actions')}
                        value={<>
                            <TooltipComponent id={`edit-entry-${entry.id}-tooltip`} text={t("edit")}>
                                <Link
                                    to={`/pve/r/rotations/${rotationId}/entries/${entry.id}/edit/`}
                                    className="btn btn-warning me-3"
                                >
                                    <i className="fa-solid fa-pen"></i>
                                </Link>
                            </TooltipComponent>
                            <TooltipComponent id={`delete-entry-${entry.id}-tooltip`} text={t("delete")}>
                                <Button variant="danger" onClick={() => setShowDeleteConfirm(true)}>
                                    <i className="fa-solid fa-trash"></i>
                                </Button>
                            </TooltipComponent>
                            <Modal
                                show={showDeleteConfirm}
                                onHide={() => setShowDeleteConfirm(false)}
                                backdrop="static"
                            >
                                <Modal.Header closeButton>
                                    <Modal.Title>{t("delete_entry")}</Modal.Title>
                                </Modal.Header>
                                <Modal.Body>
                                    <p><b>{t("delete_entry_confirmation")}</b></p>
                                </Modal.Body>
                                <Modal.Footer>
                                    <Button variant="primary" onClick={() => setShowDeleteConfirm(false)}>
                                        {t("cancel")}
                                    </Button>
                                    <Button
                                        variant="danger"
                                        className="ms-2"
                                        onClick={handleDelete}
                                    >
                                        {deleting ? <Loading size="sm" /> : t("confirm")}
                                    </Button>
                                </Modal.Footer>
                            </Modal>
                        </>}
                    />
                )}
            </CardGroup>
        </Col>
    </>
}
