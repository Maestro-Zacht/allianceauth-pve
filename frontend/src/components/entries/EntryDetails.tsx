import { useNavigate, useParams } from "react-router"
import EntryInfo from "./EntryInfo";
import { Button, Col, Container, Modal, Row } from "react-bootstrap";
import EntryShares from "./EntryShares";
import EntryRoles from "./EntryRoles";
import { deleteEntry, getEntry } from "../../api/api";
import { useQuery } from "@tanstack/react-query";
import Loading from "../Loading";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import { useToast } from "../../providers/ToastProvider";
import NavBackButton from "../NavBackButton";

export default function EntryDetails() {
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [deleting, setDeleting] = useState(false);
    const { t } = useTranslation();
    const navigate = useNavigate();
    const addToast = useToast();
    const { entryId, rotationId } = useParams();
    const entryIdNum = Number(entryId);
    const rotationIdNum = Number(rotationId);

    const { data, error, isLoading } = useQuery({
        queryKey: ['entry', rotationIdNum, entryIdNum],
        queryFn: () => getEntry(rotationIdNum, entryIdNum),
    });

    if (error) {
        console.error("Error loading entry data:", error);
        return <div>Error loading entry data.</div>;
    }

    const handleDelete = async () => {
        setDeleting(true);

        try {
            await deleteEntry(rotationIdNum, entryIdNum);
            navigate(`/pve/r/rotations/${rotationIdNum}/`);
        } catch (error) {
            addToast(error as string, "danger");
        }
        finally {
            setDeleting(false);
            setShowDeleteConfirm(false);
        }
    }

    return <>
        <NavBackButton url={`/pve/r/rotations/${rotationIdNum}/`} />
        <Container fluid>
            <Row>
                {isLoading ? (
                    <div className="text-center my-3"><Loading /></div>
                ) : (
                    <EntryInfo entry={data!} />
                )}
                <EntryRoles rotationId={rotationIdNum} entryId={entryIdNum} />
                <EntryShares rotationId={rotationIdNum} entryId={entryIdNum} />

                {!isLoading && data!.user_can_edit && <>
                    <Col xs={12}>
                        <div className="d-flex flex-row-reverse">
                            <Button variant="danger" onClick={() => setShowDeleteConfirm(true)}>
                                Delete
                            </Button>
                            <Button
                                variant="warning"
                                className="me-2"
                                href="#"
                                onClick={(e) => {
                                    e.preventDefault();
                                    alert("Edit TODO");
                                }}
                            >
                                {t("edit")}
                            </Button>
                        </div>
                    </Col>
                </>}
            </Row>
        </Container>
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
    </>
}