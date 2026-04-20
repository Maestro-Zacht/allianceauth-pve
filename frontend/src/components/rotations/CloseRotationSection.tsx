import { Alert, Button, Form, Image, Modal } from "react-bootstrap";
import { useTranslation } from "react-i18next";
import { useState, type SetStateAction, type Dispatch, Fragment } from "react";
import type { components, operations } from "../../api/Schema";
import type { i18n, TFunction } from "i18next";
import z from "zod";
import { parseLocalizedNumber } from "../../utils";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import Loading from "../Loading";
import { useToast } from "../../providers/ToastProvider";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { closeRotation, getRotationItems } from "../../api/api";
import { useNavigate } from "react-router";
import TooltipComponent from "../TooltipComponent";


type CloseRotationData = components["schemas"]["CloseRotationSchema"];
type CloseRotationError = operations["allianceauth_pve_api_rotations_close_rotation"]["responses"][400]["content"]["application/json"];
type ItemType = components["schemas"]["ItemSchema"];

const getCloseRotationSchema = (t: TFunction<"translation", undefined>, i18n: i18n, itemIds: number[]) => {
    const idsSet = new Set(itemIds);

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
        item_sales: z.array(
            z.object({
                item_id: z.coerce.number().refine((id) => idsSet.has(id), { message: t("forms.invalid_choice") }),
                sale_value: z.preprocess(
                    (value) => {
                        if (typeof value === "number") return value;
                        if (typeof value === "string") return parseLocalizedNumber(value, i18n.language);
                        return NaN;
                    },
                    z.number({ message: t("forms.number") })
                        .int({ message: t("forms.integer") })
                        .min(0, { message: t("forms.min_value", { min: 0 }) }),
                )
            })
        ),
    }) satisfies z.ZodType<CloseRotationData>;
}

interface CloseRotationFormProps {
    rotationId: number;
    showForm: boolean;
    setShowForm: Dispatch<SetStateAction<boolean>>;
    items: ItemType[];
}

function CloseRotationForm({ rotationId, showForm, setShowForm, items }: CloseRotationFormProps) {
    const { t, i18n } = useTranslation();
    const queryClient = useQueryClient();
    const closeRotationSchema = getCloseRotationSchema(t, i18n, items.map(item => item.id));
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
                if (errors.sales_value) {
                    setError("sales_value", { message: errors.sales_value.join(" ") });
                }
                if (errors.item_sales) {
                    for (const [index, itemErrors] of Object.entries(errors.item_sales)) {
                        const fieldName = `item_sales.${parseInt(index)}.sale_value` as const;
                        if (itemErrors.sale_value) {
                            setError(fieldName, { message: itemErrors.sale_value.join("\n") });
                        }
                    }
                }
                if (errors.items_missing && errors.items_missing.length > 0) {
                    setError("root", { message: t("close_rotation_missing_items", { items: errors.items_missing.join(", ") }) });
                }
            }
        }
    });

    const onSubmit = (data: CloseRotationData) => {
        console.log("Submitting close rotation with data:", data);
        mutation.mutate(data);
    }

    return <>
        <Modal show={showForm} onHide={() => setShowForm(false)} backdrop="static">
            <Modal.Header closeButton>
                <Modal.Title>{t("close_rotation")}</Modal.Title>
            </Modal.Header>
            <Form onSubmit={handleSubmit(onSubmit)}>
                <Modal.Body>
                    <Form.Group className="mb-4" controlId="sales_value">
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

                    {items.map((item, index) => (
                        <Fragment key={item.id}>
                            <Form.Group className="mb-4" controlId={`item_sales.${index}.sale_value`}>
                                <Form.Label>
                                    <Image
                                        src={`${item.icon_url}?size=32`}
                                        alt={item.name}
                                        rounded width={32} height={32}
                                        className="me-2"
                                    />
                                    {item.name}
                                </Form.Label>
                                <Controller
                                    control={control}
                                    name={`item_sales.${index}.sale_value` as const}
                                    render={({ field: { onChange, value, ref, ...field } }) => (
                                        <Form.Control
                                            ref={ref}
                                            type="text"
                                            placeholder={item.name}
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
                                            isInvalid={!!errors.item_sales?.[index]?.sale_value}
                                            {...field}
                                        />
                                    )}
                                />
                                <Form.Control.Feedback type="invalid">
                                    {errors.item_sales?.[index]?.sale_value?.message}
                                </Form.Control.Feedback>
                            </Form.Group>
                            <Form.Control hidden type="number" value={item.id} {...control.register(`item_sales.${index}.item_id` as const)} />
                        </Fragment>
                    ))}

                    {errors.root &&
                        <Alert variant="danger">
                            {errors.root.message}
                        </Alert>}
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
    const { data, isLoading, error } = useQuery({
        queryKey: ["rotation", rotationId, "items"],
        queryFn: () => getRotationItems(rotationId),
    });

    if (error) {
        console.error(error);
        return <div>Error loading rotation items</div>;
    }

    const items = data || [];

    return <>
        <TooltipComponent id="close-rotation-tooltip" text={t("close_rotation")}>
            <Button variant="danger" onClick={() => setShowCloseForm(true)}>
                {isLoading && showCloseForm ?
                    <Loading size="sm" /> :
                    <i className="fa-solid fa-hand-holding-dollar"></i>}
            </Button>
        </TooltipComponent>
        {!isLoading && <CloseRotationForm
            rotationId={rotationId}
            showForm={showCloseForm}
            setShowForm={setShowCloseForm}
            items={items}
        />}
    </>
}
