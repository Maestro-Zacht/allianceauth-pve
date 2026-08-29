import DataTableComponent from 'datatables.net-react';
import type { DataTableProps, DataTableRef } from 'datatables.net-react';
import DataTablesCore from 'datatables.net-bs5';
import type { ColumnsConfig, Options } from 'datatables.net-bs5';
import 'datatables.net-columncontrol-bs5';
import type { ForwardRefExoticComponent, RefAttributes } from 'react';

import "./DataTables.css";

// eslint-disable-next-line react-hooks/rules-of-hooks -- DataTable.use registers the core plugin, not a React hook
DataTableComponent.use(DataTablesCore);

// DataTables 3.0 renamed its option interfaces `Config` -> `Options` and
// `ConfigColumns` -> `ColumnsConfig`, but datatables.net-columncontrol@2 still
// augments the old names and datatables.net-react@1 still types `options`,
// `columns` and `ajax` in terms of `Config`. Because TypeScript creates a name
// that an augmentation targets but the module no longer exports, `Config` ends
// up as a phantom interface holding only `columnControl` — so every real option
// is rejected and `columns`/`ajax` silently degrade to an error type.
// Re-point those props at the real DataTables 3 types.
// Remove once upstream updates to the DataTables 3 names.
type DataTableFixedProps = Omit<DataTableProps, 'ajax' | 'columns' | 'options'> & {
    ajax?: Options['ajax'];
    columns?: Options['columns'] | ColumnsConfig[];
    options?: Options;
};

const DataTable = DataTableComponent as unknown as ForwardRefExoticComponent<
    DataTableFixedProps & RefAttributes<DataTableRef>
>;

export default DataTable;
