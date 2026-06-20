import DataTable from 'datatables.net-react';
import DataTablesCore from 'datatables.net-bs5';
import 'datatables.net-columncontrol-bs5';

import "./DataTables.css";

// eslint-disable-next-line react-hooks/rules-of-hooks -- DataTable.use registers the core plugin, not a React hook
DataTable.use(DataTablesCore);

export default DataTable;
