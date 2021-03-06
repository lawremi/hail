import unittest
import hail as hl
import hail.ir as ir
from hail.utils.java import Env
from hail.utils import new_temp_file
from .helpers import *

setUpModule = startTestHailContext
tearDownModule = stopTestHailContext


class ValueIRTests(unittest.TestCase):
    def value_irs(self):
        b = ir.TrueIR()
        c = ir.Ref('c')
        i = ir.I32(5)
        j = ir.I32(7)
        st = ir.Str('Hail')
        a = ir.Ref('a')
        aa = ir.Ref('aa')
        da = ir.Ref('da')
        nd = ir.Ref('nd')
        v = ir.Ref('v')
        s = ir.Ref('s')
        t = ir.Ref('t')
        call = ir.Ref('call')

        table = ir.TableRange(5, 3)

        matrix_read = ir.MatrixRead(ir.MatrixNativeReader(
            resource('backward_compatability/1.0.0/matrix_table/0.hmt')), False, False)

        block_matrix_read = ir.BlockMatrixRead('fake_file_path')

        value_irs = [
            i, ir.I64(5), ir.F32(3.14), ir.F64(3.14), s, ir.TrueIR(), ir.FalseIR(), ir.Void(),
            ir.Cast(i, hl.tfloat64),
            ir.NA(hl.tint32),
            ir.IsNA(i),
            ir.If(b, i, j),
            ir.Let('v', i, v),
            ir.Ref('x'),
            ir.ApplyBinaryOp('+', i, j),
            ir.ApplyUnaryOp('-', i),
            ir.ApplyComparisonOp('EQ', i, j),
            ir.MakeArray([i, ir.NA(hl.tint32), ir.I32(-3)], hl.tarray(hl.tint32)),
            ir.ArrayRef(a, i),
            ir.ArrayLen(a),
            ir.ArrayRange(ir.I32(0), ir.I32(5), ir.I32(1)),
            ir.ArraySort(a, 'l', 'r', ir.ApplyComparisonOp("LT", ir.Ref('l'), ir.Ref('r'))),
            ir.ToSet(a),
            ir.ToDict(da),
            ir.ToArray(a),
            ir.MakeNDArray(ir.MakeArray([ir.F64(-1.0), ir.F64(1.0)], hl.tarray(hl.tfloat64)),
                           ir.MakeArray([ir.I64(1), ir.I64(2)], hl.tarray(hl.tint64)),
                           ir.TrueIR()),
            ir.NDArrayRef(nd, ir.MakeArray([ir.I64(1), ir.I64(2)], hl.tarray(hl.tint64))),
            ir.LowerBoundOnOrderedCollection(a, i, True),
            ir.GroupByKey(da),
            ir.ArrayMap(a, 'v', v),
            ir.ArrayFilter(a, 'v', v),
            ir.ArrayFlatMap(aa, 'v', v),
            ir.ArrayFold(a, ir.I32(0), 'x', 'v', v),
            ir.ArrayScan(a, ir.I32(0), 'x', 'v', v),
            ir.ArrayLeftJoinDistinct(a, a, 'l', 'r', ir.I32(0), ir.I32(1)),
            ir.ArrayFor(a, 'v', ir.Void()),
            ir.AggFilter(ir.TrueIR(), ir.I32(0)),
            ir.AggExplode(ir.ArrayRange(ir.I32(0), ir.I32(2), ir.I32(1)), 'x', ir.I32(0)),
            ir.AggGroupBy(ir.TrueIR(), ir.I32(0)),
            ir.AggArrayPerElement(ir.ArrayRange(ir.I32(0), ir.I32(2), ir.I32(1)), 'x', ir.I32(0)),
            ir.ApplyAggOp('Collect', [], None, [ir.I32(0)]),
            ir.ApplyScanOp('Collect', [], None, [ir.I32(0)]),
            ir.ApplyAggOp('Histogram', [ir.F64(-5.0), ir.F64(5.0), ir.I32(100)], None, [ir.F64(-2.11)]),
            ir.ApplyAggOp('CallStats', [], [ir.I32(2)], [call]),
            ir.ApplyAggOp('TakeBy', [ir.I32(10)], None, [ir.F64(-2.11), ir.F64(-2.11)]),
            ir.Begin([ir.Void()]),
            ir.MakeStruct([('x', i)]),
            ir.SelectFields(s, ['x', 'z']),
            ir.InsertFields(s, [('x', i)], None),
            ir.GetField(s, 'x'),
            ir.MakeTuple([i, b]),
            ir.GetTupleElement(t, 1),
            ir.StringSlice(st, ir.I32(1), ir.I32(2)),
            ir.StringLength(st),
            ir.In(2, hl.tfloat64),
            ir.Die(ir.Str('mumblefoo'), hl.tfloat64),
            ir.Apply('&&', b, c),
            ir.Apply('toFloat64', i),
            ir.Uniroot('x', ir.F64(3.14), ir.F64(-5.0), ir.F64(5.0)),
            ir.Literal(hl.tarray(hl.tint32), [1, 2, None]),
            ir.TableCount(table),
            ir.TableGetGlobals(table),
            ir.TableCollect(table),
            ir.TableToValueApply(table, {'name': 'ForceCountTable'}),
            ir.MatrixToValueApply(matrix_read, {'name': 'ForceCountMatrixTable'}),
            ir.TableAggregate(table, ir.MakeStruct([('foo', ir.ApplyAggOp('Collect', [], None, [ir.I32(0)]))])),
            ir.TableWrite(table, new_temp_file(), False, True, "fake_codec_spec$$"),
            ir.TableExport(table, new_temp_file(), None, True, 0, ","),
            ir.MatrixAggregate(matrix_read, ir.MakeStruct([('foo', ir.ApplyAggOp('Collect', [], None, [ir.I32(0)]))])),
            ir.MatrixWrite(matrix_read, ir.MatrixNativeWriter(new_temp_file(), False, False, "")),
            ir.MatrixWrite(matrix_read, ir.MatrixVCFWriter(new_temp_file(), None, False, None)),
            ir.MatrixWrite(matrix_read, ir.MatrixGENWriter(new_temp_file(), 4)),
            ir.MatrixWrite(matrix_read, ir.MatrixPLINKWriter(new_temp_file())),
            ir.MatrixMultiWrite([matrix_read, matrix_read], ir.MatrixNativeMultiWriter(new_temp_file(), False, False)),
            ir.BlockMatrixWrite(block_matrix_read, 'fake_file_path', False, False, False)
        ]

        return value_irs

    def test_parses(self):
        env = {'c': hl.tbool,
               'a': hl.tarray(hl.tint32),
               'aa': hl.tarray(hl.tarray(hl.tint32)),
               'da': hl.tarray(hl.ttuple(hl.tint32, hl.tstr)),
               'nd': hl.tndarray(hl.tfloat64),
               'v': hl.tint32,
               's': hl.tstruct(x=hl.tint32, y=hl.tint64, z=hl.tfloat64),
               't': hl.ttuple(hl.tint32, hl.tint64, hl.tfloat64),
               'call': hl.tcall,
               'x': hl.tint32}
        env = {name: t._parsable_string() for name, t in env.items()}
        for x in self.value_irs():
            Env.hail().expr.ir.IRParser.parse_value_ir(str(x), env, {})

    def test_copies(self):
        for x in self.value_irs():
            self.assertEqual(x, x.copy(*x.children))


class TableIRTests(unittest.TestCase):

    def table_irs(self):
        b = ir.TrueIR()
        table_read = ir.TableRead(
            ir.TableNativeReader(resource('backward_compatability/1.0.0/table/0.ht')), False)
        table_read_row_type = hl.dtype('struct{idx: int32, f32: float32, i64: int64, m: float64, astruct: struct{a: int32, b: float64}, mstruct: struct{x: int32, y: str}, aset: set<str>, mset: set<float64>, d: dict<array<str>, float64>, md: dict<int32, str>, h38: locus<GRCh38>, ml: locus<GRCh37>, i: interval<locus<GRCh37>>, c: call, mc: call, t: tuple(call, str, str), mt: tuple(locus<GRCh37>, bool)}')

        matrix_read = ir.MatrixRead(
            ir.MatrixNativeReader(resource('backward_compatability/1.0.0/matrix_table/0.hmt')), False, False)

        range = ir.TableRange(10, 4)
        table_irs = [
            ir.TableKeyBy(table_read, ['m', 'd'], False),
            ir.TableFilter(table_read, b),
            table_read,
            ir.MatrixColsTable(matrix_read),
            ir.TableAggregateByKey(
                table_read,
                ir.MakeStruct([('a', ir.I32(5))])),
            ir.TableKeyByAndAggregate(
                table_read,
                ir.MakeStruct([('a', ir.I32(5))]),
                ir.MakeStruct([('b', ir.I32(5))]),
                1, 2),
            ir.TableJoin(
                table_read,
                ir.TableRange(100, 10), 'inner', 1),
            ir.MatrixEntriesTable(matrix_read),
            ir.MatrixRowsTable(matrix_read),
            ir.TableParallelize(ir.MakeStruct([
                ('rows', ir.Literal(hl.tarray(hl.tstruct(a=hl.tint32)), [{'a':None}, {'a':5}, {'a':-3}])),
                ('global', ir.MakeStruct([]))]), None),
            ir.TableMapRows(
                ir.TableKeyBy(table_read, []),
                ir.MakeStruct([
                    ('a', ir.GetField(ir.Ref('row'), 'f32')),
                    ('b', ir.F64(-2.11))])),
            ir.TableMapGlobals(
                table_read,
                ir.MakeStruct([
                    ('foo', ir.NA(hl.tarray(hl.tint32)))])),
            ir.TableRange(100, 10),
            ir.TableRepartition(table_read, 10, ir.RepartitionStrategy.COALESCE),
            ir.TableUnion(
                [ir.TableRange(100, 10), ir.TableRange(50, 10)]),
            ir.TableExplode(table_read, ['mset']),
            ir.TableHead(table_read, 10),
            ir.TableOrderBy(ir.TableKeyBy(table_read, []), [('m', 'A'), ('m', 'D')]),
            ir.TableDistinct(table_read),
            ir.CastMatrixToTable(matrix_read, '__entries', '__cols'),
            ir.TableRename(table_read, {'idx': 'idx_foo'}, {'global_f32': 'global_foo'}),
            ir.TableMultiWayZipJoin([table_read, table_read], '__data', '__globals'),
            ir.MatrixToTableApply(matrix_read, {'name': 'LinearRegressionRowsSingle', 'yFields': ['col_m'], 'xField': 'entry_m', 'covFields': [], 'rowBlockSize': 10, 'passThrough': []}),
            ir.TableToTableApply(table_read, {'name': 'TableFilterPartitions', 'parts': [0], 'keep': True})
        ]

        return table_irs

    def test_parses(self):
        for x in self.table_irs():
            Env.hail().expr.ir.IRParser.parse_table_ir(str(x))

    def test_matrix_ir_parses(self):
        hl.index_bgen(resource('example.8bits.bgen'),
                      reference_genome=hl.get_reference('GRCh37'),
                      contig_recoding={'01': '1'})

        collect = ir.MakeStruct([('x', ir.ApplyAggOp('Collect', [], None, [ir.I32(0)]))])

        matrix_read = ir.MatrixRead(
            ir.MatrixNativeReader(resource('backward_compatability/1.0.0/matrix_table/0.hmt')), False, False)
        table_read = ir.TableRead(
            ir.TableNativeReader(resource('backward_compatability/1.0.0/table/0.ht')), False)

        matrix_range = ir.MatrixRead(ir.MatrixRangeReader(1, 1, 10))
        matrix_irs = [
            ir.MatrixRepartition(matrix_range, 100, ir.RepartitionStrategy.SHUFFLE),
            ir.MatrixUnionRows(matrix_range, matrix_range),
            ir.MatrixDistinctByRow(matrix_range),
            ir.MatrixRowsHead(matrix_read, 5),
            ir.CastTableToMatrix(
                ir.CastMatrixToTable(matrix_read, '__entries', '__cols'),
                '__entries',
                '__cols',
                []),
            ir.MatrixAggregateRowsByKey(matrix_read, collect, collect),
            ir.MatrixAggregateColsByKey(matrix_read, collect, collect),
            matrix_read,
            matrix_range,
            ir.MatrixRead(ir.MatrixVCFReader(resource('sample.vcf'), ['GT'], hl.tfloat64, None, None, None, None,
                                             False, True, False, True, None, None, None)),
            ir.MatrixRead(ir.MatrixBGENReader(resource('example.8bits.bgen'), None, {}, 10, 1, None)),
            ir.MatrixFilterRows(matrix_read, ir.FalseIR()),
            ir.MatrixFilterCols(matrix_read, ir.FalseIR()),
            ir.MatrixFilterEntries(matrix_read, ir.FalseIR()),
            ir.MatrixChooseCols(matrix_read, [1, 0]),
            ir.MatrixMapCols(matrix_read, ir.MakeStruct([('x', ir.I64(20))]), ['x']),
            ir.MatrixKeyRowsBy(matrix_read, ['row_i64'], False),
            ir.MatrixMapRows(ir.MatrixKeyRowsBy(matrix_read, []), ir.MakeStruct([('x', ir.I64(20))])),
            ir.MatrixMapEntries(matrix_read, ir.MakeStruct([('x', ir.I64(20))])),
            ir.MatrixMapGlobals(matrix_read, ir.MakeStruct([('x', ir.I64(20))])),
            ir.MatrixCollectColsByKey(matrix_read),
            ir.MatrixExplodeRows(matrix_read, ['row_aset']),
            ir.MatrixExplodeCols(matrix_read, ['col_aset']),
            ir.MatrixAnnotateRowsTable(matrix_read, table_read, '__foo'),
            ir.MatrixAnnotateColsTable(matrix_read, table_read, '__foo'),
            ir.MatrixToMatrixApply(matrix_read, {'name': 'MatrixFilterPartitions', 'parts': [0], 'keep': True})
        ]


        for x in matrix_irs:
            try:
                Env.hail().expr.ir.IRParser.parse_matrix_ir(str(x))
            except Exception as e:
                raise ValueError(str(x)) from e


class BlockMatrixIRTests(unittest.TestCase):
    @staticmethod
    def _make_element_wise_op_ir(bm1, bm2, op):
        return ir.BlockMatrixMap2(bm1, bm2, ir.ApplyBinaryOp(op, ir.Ref("l"), ir.Ref("r")))

    def block_matrix_irs(self):
        scalar_ir = ir.F64(2)
        vector_ir = ir.MakeArray([ir.F64(3), ir.F64(2)], hl.tarray(hl.tfloat64))

        read = ir.BlockMatrixRead(resource('blockmatrix_example/0'))
        add_two_bms = BlockMatrixIRTests._make_element_wise_op_ir(read, read, '+')

        scalar_to_bm = ir.ValueToBlockMatrix(scalar_ir, [], 1, [])
        vector_to_bm = ir.ValueToBlockMatrix(vector_ir, [2], 1, [False])
        broadcast_scalar = ir.BlockMatrixBroadcast(scalar_to_bm, "scalar", [2, 2], 256, [False, False])
        broadcast_col = ir.BlockMatrixBroadcast(vector_to_bm, "col", [2, 2], 256, [False, False])
        broadcast_row = ir.BlockMatrixBroadcast(vector_to_bm, "row", [2, 2], 256, [False, False])

        return [
            read,
            add_two_bms,
            scalar_to_bm,
            vector_to_bm,
            broadcast_scalar,
            broadcast_col,
            broadcast_row,
        ]

    def test_parses(self):
        for x in self.block_matrix_irs():
            Env.hail().expr.ir.IRParser.parse_blockmatrix_ir(str(x))


class ValueTests(unittest.TestCase):

    def values(self):
        values = [
            (hl.tbool, True),
            (hl.tint32, 0),
            (hl.tint64, 0),
            (hl.tfloat32, 0.5),
            (hl.tfloat64, 0.5),
            (hl.tstr, "foo"),
            (hl.tstruct(x=hl.tint32), hl.Struct(x=0)),
            (hl.tarray(hl.tint32), [0, 1, 4]),
            (hl.tset(hl.tint32), {0, 1, 4}),
            (hl.tdict(hl.tstr, hl.tint32), {"a": 0, "b": 1, "c": 4}),
            (hl.tinterval(hl.tint32), hl.Interval(0, 1, True, False)),
            (hl.tlocus(hl.default_reference()), hl.Locus("1", 1)),
            (hl.tcall, hl.Call([0, 1]))
        ]
        return values

    def test_value_same_after_parsing(self):
        for t, v in self.values():
            row_v = ir.Literal(t, v)
            map_globals_ir = ir.TableMapGlobals(
                ir.TableRange(1, 1),
                ir.InsertFields(
                    ir.Ref("global"),
                    [("foo", row_v)],
                    None))
            new_globals = hl.eval(hl.Table(map_globals_ir).globals)
            self.assertEquals(new_globals, hl.Struct(foo=v))
