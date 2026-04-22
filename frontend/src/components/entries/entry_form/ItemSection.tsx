import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { searchItems } from "../../../api/api";
import Loading from "../../Loading";
import { useTranslation } from "react-i18next";
import { Button, Modal, Form, ListGroup, Image, Row, Col, Offcanvas, FloatingLabel } from "react-bootstrap";
import type { ExtendedEntryItem } from "../EntryTypes";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import { parseLocalizedNumber } from "../../../utils";


function ItemModal() {
    const { t } = useTranslation();
    const [show, setShow] = useState(false);
    const [pasteData, setPasteData] = useState("");
    const [items, setItems] = useState<ExtendedEntryItem[] | null>(null);
    const mutation = useMutation({
        mutationFn: searchItems,
        onSuccess: (data) => {
            setItems(data);
            setPasteData("");
        },
        onError: (error) => {
            alert("Error: " + error);
        }
    });
    const { updateEntryData } = useEntryProcessor();

    const handleClose = () => {
        setShow(false);
        setItems(null);
    };

    return <>
        <Button onClick={() => setShow(true)}>
            {t("add")}
        </Button>
        <Modal
            show={show}
            backdrop="static"
            onHide={handleClose}
        >
            <Modal.Header closeButton>
                <Modal.Title>{t("paste_loot_items")}</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                {items === null ? <>
                    <Form.Group controlId="pasteData">
                        <Form.Control
                            as="textarea"
                            rows={15}
                            value={pasteData}
                            onChange={(e) => setPasteData(e.target.value)}
                            placeholder={t("paste_loot_items")}
                        />
                    </Form.Group>
                </> : <>
                    <ListGroup variant="flush">
                        {items.map(item => (
                            <ListGroup.Item key={item.id} className="d-flex align-items-center justify-content-between">
                                <div>
                                    <Image
                                        src={`${item.icon_url}?size=32`}
                                        alt={item.name}
                                        rounded width={32} height={32}
                                        className="me-2"
                                    />
                                    {item.name}
                                </div>
                                <span>{t("quantity_num", { quantity: item.quantity })}</span>
                            </ListGroup.Item>
                        ))}
                    </ListGroup>
                </>}
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={handleClose}>
                    {t("cancel")}
                </Button>
                {items === null ? <>
                    <Button
                        variant="primary"
                        disabled={mutation.isPending}
                        onClick={() => {
                            mutation.mutate(pasteData);
                        }}
                    >
                        {mutation.isPending ? <Loading size="sm" /> : t("load")}
                    </Button>
                </> : <>
                    <Button variant="warning" onClick={() => {
                        updateEntryData({ type: 'replace_items', items });
                        handleClose();
                    }}>
                        {t("replace")}
                    </Button>
                    <Button onClick={() => {
                        updateEntryData({ type: 'add_items', items });
                        handleClose();
                    }}>
                        {t("add")}
                    </Button>
                </>}
            </Modal.Footer>
        </Modal>
    </>
}

interface ItemSectionProps {
    items: ExtendedEntryItem[];
}

export default function ItemSection({ items }: ItemSectionProps) {
    const { t, i18n } = useTranslation();
    const [show, setShow] = useState(false);
    const { updateEntryData } = useEntryProcessor();

    const localizeNumber = (num: number) => {
        return num.toLocaleString(i18n.language, { maximumFractionDigits: 0 });
    }

    return <>
        <Row className="mb-3">
            <Col sm={2}>{t("loot_items")}</Col>
            <Col sm={6} className="text-center">{t("items_count", { count: items.length })}</Col>
            <Col sm={4} className="text-end">
                <Button onClick={() => setShow(true)}>
                    {t("show")}
                </Button>
                <Offcanvas show={show} onHide={() => setShow(false)} placement="end">
                    <Offcanvas.Header closeButton>
                        <Offcanvas.Title>{t("loot_items")}</Offcanvas.Title>
                    </Offcanvas.Header>
                    <Offcanvas.Body>
                        {items.length === 0 ? <p>{t("no_loot_items")}</p> :
                            <ListGroup variant="flush" className="mb-3">
                                {items.map(item => (
                                    <ListGroup.Item key={item.id} className="d-flex align-items-center justify-content-between">
                                        <div>
                                            <Image
                                                src={`${item.icon_url}?size=32`}
                                                alt={item.name}
                                                rounded width={32} height={32}
                                                className="me-2"
                                            />
                                            {item.name}
                                        </div>
                                        <FloatingLabel controlId={`quantity-${item.id}`} label={t("quantity")} style={{ width: '35%' }}>
                                            <Form.Control
                                                type="text"
                                                value={localizeNumber(item.quantity)}
                                                onChange={(e) => {
                                                    const newQuantity = parseLocalizedNumber(e.target.value, i18n.language);
                                                    if (e.target.value === '') {
                                                        updateEntryData({ type: 'update_item_quantity', item_id: item.id, quantity: 1 });
                                                    }
                                                    else if (!isNaN(newQuantity) && newQuantity >= 1) {
                                                        updateEntryData({ type: 'update_item_quantity', item_id: item.id, quantity: newQuantity });
                                                    }
                                                }}
                                            />
                                        </FloatingLabel>
                                    </ListGroup.Item>
                                ))}
                            </ListGroup>
                        }
                        <ItemModal />
                    </Offcanvas.Body>
                </Offcanvas>
            </Col>
        </Row>
    </>
}