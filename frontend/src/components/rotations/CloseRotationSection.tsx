import { Button, Form, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { useState, type SetStateAction, type Dispatch } from "react";
import type { components, operations } from "../../api/Schema";
import type { i18n, TFunction } from "i18next";
import z from "zod";
import { parseLocalizedNumber } from "../../utils";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Loading from "../Loading";
import { useToast } from "../../providers/ToastProvider";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { closeRotation } from "../../api/api";
import { useNavigate } from "react-router";
import TooltipComponent from "../TooltipComponent";


type CloseRotationData = components["schemas"]["CloseRotationSchema"];
type CloseRotationError = operations["allianceauth_pve_api_rotations_close_rotation"]["responses"][400]["content"]["application/json"];

const getCloseRotationSchema = (t: TFunction<"translation", undefined>, i18n: i18n) => {
    return z.object({
        sales_value: z.preprocess(
            (value) => {
                if (typeof value === "number") return value;
                if (typeof value === "string") return parseLocalizedNumber(value, i18n.language);
                return NaN;
            },
            z.number({ message: t("forms.number") })
                .int({ message: t("forms.integer") })
                .min(0, { message: t("forms.min_value", { min: 0 }) }),
        ),
    }) satisfies z.ZodType<CloseRotationData>;
}

interface CloseRotationFormProps {
    rotationId: number;
    showForm: boolean;
    setShowForm: Dispatch<SetStateAction<boolean>>;
}

function CloseRotationForm({ rotationId, showForm, setShowForm }: CloseRotationFormProps) {
    const { t, i18n } = useTranslation();
    const queryClient = useQueryClient();
    const closeRotationSchema = getCloseRotationSchema(t, i18n);
    const {
        control,
        handleSubmit,
        setError,
        formState: { errors },
    } = useForm({
        resolver: zodResolver(closeRotationSchema),
    });
    const addToast = useToast();
    const navigate = useNavigate();
    const mutation = useMutation({
        mutationFn: (data: CloseRotationData) => closeRotation(rotationId, data),
        onSuccess: () => {
            addToast(t("rotation_closed"));
            setShowForm(false);
            queryClient.invalidateQueries({ queryKey: ["rotation", rotationId] });
        },
        onError: (errors: CloseRotationError | number) => {
            if (typeof errors === "number") {
                if (errors === 404) {
                    addToast(t("rotation_not_found"), "danger");
                    navigate("/pve/r/");
                } else if (errors === 403) {
                    addToast(t("no_permission"), "danger");
                    setShowForm(false);
                    queryClient.invalidateQueries({ queryKey: ["rotation", rotationId] });
                    queryClient.invalidateQueries({ queryKey: ["permissions"] });
                } else {
                    addToast(t("unknown_error"), "danger");
                }
            } else {
                Object.entries(errors).forEach(([field, messages]) => {
                    setError(field as keyof CloseRotationData, { type: "server", message: messages.join(" - ") });
                })
            }
        }
    });

    const onSubmit = (data: CloseRotationData) => {
        mutation.mutate(data);
    }

    return <>
        <Modal show={showForm} onHide={() => setShowForm(false)} backdrop="static">
            <Modal.Header closeButton>
                <Modal.Title>{t("close_rotation")}</Modal.Title>
            </Modal.Header>
            <Form onSubmit={handleSubmit(onSubmit)}>
                <Modal.Body>
                    <Form.Group className="mb-3" controlId="sales_value">
                        <Form.Label>{t("sales_value")}</Form.Label>
                        <Controller
                            control={control}
                            name="sales_value"
                            render={({ field: { onChange, value, ref, ...field } }) => (
                                <Form.Control
                                    ref={ref}
                                    type="text"
                                    placeholder={t("sales_value")}
                                    value={value === undefined ? "" : value as string}
                                    onChange={(e) => {
                                        const rawTypedValue = e.target.value;
                                        const rawNumber = parseLocalizedNumber(rawTypedValue, i18n.language);
                                        if (isNaN(rawNumber)) {
                                            onChange(rawTypedValue);
                                        }
                                        else {
                                            const formattedValue = rawNumber.toLocaleString(i18n.language);
                                            onChange(formattedValue);
                                        }
                                    }}
                                    isInvalid={!!errors.sales_value}
                                    {...field}
                                />
                            )}
                        />
                        <Form.Control.Feedback type="invalid">
                            {errors.sales_value?.message}
                        </Form.Control.Feedback>
                    </Form.Group>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="danger" onClick={() => setShowForm(false)}>
                        {t("cancel")}
                    </Button>
                    <Button variant="primary" type="submit" disabled={mutation.isPending}>
                        {mutation.isPending ? <Loading size="sm" /> : t("submit")}
                    </Button>
                </Modal.Footer>
            </Form>
        </Modal>
    </>
}

interface CloseRotationSectionProps {
    rotationId: number;
}

export default function CloseRotationSection({ rotationId }: CloseRotationSectionProps) {
    const { t } = useTranslation();
    const [showCloseForm, setShowCloseForm] = useState(false);

    return <>
        <TooltipComponent id="close-rotation-tooltip" text={t("close_rotation")}>
            <Button variant="danger" onClick={() => setShowCloseForm(true)}>
                <i className="fa-solid fa-hand-holding-dollar"></i>
            </Button>
        </TooltipComponent>
        <CloseRotationForm
            rotationId={rotationId}
            showForm={showCloseForm}
            setShowForm={setShowCloseForm}
        />
    </>
}
