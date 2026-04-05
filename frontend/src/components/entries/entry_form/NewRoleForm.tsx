import type { TFunction } from "i18next";
import type { ExtendedEntryFormSchema } from "../EntryTypes";
import z from "zod";
import { useTranslation } from "react-i18next";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { useEntryProcessor } from "../../../providers/EntryFormProvider";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button, Col, Form, Modal, Row } from "react-bootstrap";

type RoleType = ExtendedEntryFormSchema["roles"][number];

const getNewRoleSchema = (t: TFunction<"translation", undefined>, roleNames: string[]) => {
    const roleNamesSet = new Set(roleNames);

    return z.object({
        name: z.string()
            .min(1, { message: t("forms.min_len", { min: 1 }) })
            .max(64, { message: t("forms.max_len", { max: 64 }) })
            .refine(roleName => !roleNamesSet.has(roleName), { message: t("forms.already_taken") }),
        value: z.number({ message: t("forms.number") })
            .int({ message: t("forms.integer") })
            .min(1, { message: t("forms.min_value", { min: 1 }) })
    }) satisfies z.ZodType<RoleType>;
}

interface NewRoleFormProps {
    existingRoleNames: string[];
}

export default function NewRoleForm({ existingRoleNames }: NewRoleFormProps) {
    const { t } = useTranslation();
    const [show, setShow] = useState(false);
    const newRoleSchema = getNewRoleSchema(t, existingRoleNames);
    const {
        register,
        handleSubmit,
        reset,
        formState: { errors },
    } = useForm<RoleType>({
        defaultValues: { value: 1 },
        resolver: zodResolver(newRoleSchema)
    });
    const { updateEntryData } = useEntryProcessor();

    const onSubmit = (data: RoleType) => {
        updateEntryData({ type: 'add_role', role: data });
        reset();
        setShow(false);
    }

    return <>
        <Button variant="success" onClick={() => setShow(true)}>
            {t("new_role")}
        </Button>
        <Modal
            show={show}
            onHide={() => setShow(false)}
            backdrop="static"
            keyboard={false}
        >
            <Modal.Header closeButton>
                <Modal.Title>{t("new_role")}</Modal.Title>
            </Modal.Header>
            <Form onSubmit={handleSubmit(onSubmit)}>
                <Modal.Body>

                    <Form.Group as={Row} className="mb-3" controlId="formRoleName">
                        <Form.Label column sm={2}>
                            {t("name")}
                        </Form.Label>
                        <Col sm={10}>
                            <Form.Control
                                type="text" placeholder={t("name")}
                                {...register("name")}
                                isInvalid={!!errors.name}
                            />
                            <Form.Control.Feedback type="invalid">
                                {errors.name?.message}
                            </Form.Control.Feedback>
                        </Col>
                    </Form.Group>

                    <Form.Group as={Row} className="mb-3" controlId="formRoleValue">
                        <Form.Label column sm={2}>
                            {t("value")}
                        </Form.Label>
                        <Col sm={10}>
                            <Form.Control
                                type="number" placeholder={t("value")}
                                {...register("value", { valueAsNumber: true })}
                                min={newRoleSchema.shape.value.minValue || undefined}
                                isInvalid={!!errors.value}
                            />
                            <Form.Control.Feedback type="invalid">
                                {errors.value?.message}
                            </Form.Control.Feedback>
                        </Col>
                    </Form.Group>

                </Modal.Body>

                <Modal.Footer>
                    <Button variant="danger" onClick={() => setShow(false)}>
                        {t("cancel")}
                    </Button>
                    <Button variant="primary" type="submit">
                        {t("confirm")}
                    </Button>
                </Modal.Footer>
            </Form>
        </Modal>
    </>
}