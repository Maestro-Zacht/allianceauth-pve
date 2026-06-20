import { useParams } from "react-router"
import EntryInfo from "./EntryInfo";
import { Row } from "react-bootstrap";
import EntryShares from "./EntryShares";
import EntryRoles from "./EntryRoles";
import { getEntry } from "../../api/api";
import { useQuery } from "@tanstack/react-query";
import Loading from "../utils/Loading";
import NavBackButton from "../utils/NavBackButton";
import EntryItems from "./EntryItems";

export default function EntryDetails() {
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

    return <>
        <NavBackButton url={`/pve/r/rotations/${rotationIdNum}/`} />
        <Row>
            {isLoading ?
                <div className="text-center my-3"><Loading /></div> :
                <EntryInfo entry={data!} rotationId={rotationIdNum} />
            }
            <EntryRoles rotationId={rotationIdNum} entryId={entryIdNum} />
            <EntryItems rotationId={rotationIdNum} entryId={entryIdNum} />
            {isLoading ?
                <div className="text-center my-3"><Loading /></div> :
                <EntryShares rotationId={rotationIdNum} entryId={entryIdNum} isRotationClosed={data!.rotation_is_closed} />
            }
        </Row>
    </>
}
