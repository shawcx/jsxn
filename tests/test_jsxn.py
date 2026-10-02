import json
import unittest

from jsxn import jsxn, _cache


class JsxnTestCase(unittest.TestCase):
    # The class cache is global, so start each test with it empty.
    def setUp(self):
        _cache.clear()

    def tearDown(self):
        _cache.clear()


class TestDynamic(JsxnTestCase):
    def test_from_dict(self):
        obj = jsxn.dynamic({'schema':100,'key':'value'})
        self.assertEqual(dict(obj), {'schema':100,'key':'value'})

    def test_from_json(self):
        obj = jsxn.dynamic('{"schema":100,"key":"value"}')
        self.assertEqual(dict(obj), {'schema':100,'key':'value'})

    def test_from_keywords(self):
        obj = jsxn.dynamic(schema=100, key='value')
        self.assertEqual(dict(obj), {'schema':100,'key':'value'})

    def test_str_is_json(self):
        obj = jsxn.dynamic({'schema':100,'key':'value'})
        self.assertEqual(json.loads(str(obj)), {'schema':100,'key':'value'})

    def test_len(self):
        self.assertEqual(len(jsxn.dynamic({'a':1,'b':2})), 2)

    def test_class_is_cached(self):
        first = jsxn.dynamic({'schema':100,'key':'value'})
        self.assertIs(jsxn.dynamic, type(first))
        self.assertIs(jsxn['dynamic'], type(first))

    def test_later_instances_use_cached_schema(self):
        jsxn.dynamic({'schema':100,'key':'value'})
        obj = jsxn.dynamic('{"schema":200}')
        self.assertEqual(dict(obj), {'schema':200,'key':None})

    def test_no_arguments_gives_nulls(self):
        jsxn.dynamic({'schema':100,'key':'value'})
        self.assertEqual(dict(jsxn.dynamic()), {'schema':None,'key':None})

    def test_empty(self):
        self.assertEqual(str(jsxn.empty()), '{}')

    @unittest.expectedFailure
    def test_from_list(self):
        # README documents this, but __call__ rejects the list as initial data.
        obj = jsxn.dynamic(['attr1','attr2'])
        self.assertEqual(dict(obj), {'attr1':None,'attr2':None})

    def test_invalid_json(self):
        with self.assertRaises(ValueError):
            jsxn.dynamic('not json')

    def test_invalid_type(self):
        with self.assertRaises(ValueError):
            jsxn.dynamic(42)

    def test_too_many_arguments(self):
        with self.assertRaises(ValueError):
            jsxn.dynamic({'a':1}, {'b':2})


class TestInstance(JsxnTestCase):
    def setUp(self):
        super().setUp()
        self.obj = jsxn.dynamic({'schema':None,'key':None})

    def test_attribute_access(self):
        self.obj.schema = 300
        self.assertEqual(self.obj['schema'], 300)

    def test_item_access(self):
        self.obj['key'] = 'populate'
        self.assertEqual(self.obj.key, 'populate')

    def test_call_with_json_and_keywords_chains(self):
        result = self.obj('{"schema":500}')(key='hello')
        self.assertIs(result, self.obj)
        self.assertEqual(dict(self.obj), {'schema':500,'key':'hello'})

    def test_call_with_instance(self):
        other = jsxn.dynamic(schema=1, key='copied')
        self.obj(other)
        self.assertEqual(dict(self.obj), {'schema':1,'key':'copied'})

    def test_unknown_attribute_rejected(self):
        with self.assertRaises(AttributeError):
            self.obj.not_defined = True

    def test_unknown_key_rejected(self):
        with self.assertRaises(AttributeError):
            self.obj('{"not_defined":true}')


class TestDelete(JsxnTestCase):
    def test_delete_attribute(self):
        jsxn.dynamic({'a':1})
        del jsxn.dynamic
        self.assertNotIn('dynamic', _cache)
        # The name can then be reused with a new schema.
        self.assertEqual(dict(jsxn.dynamic({'b':2})), {'b':2})

    def test_delete_item(self):
        jsxn.dynamic({'a':1})
        del jsxn['dynamic']
        self.assertNotIn('dynamic', _cache)

    def test_delete_missing_attribute(self):
        with self.assertRaises(AttributeError):
            del jsxn.missing


class TestDecorator(JsxnTestCase):
    def test_annotations(self):
        @jsxn
        class example:
            first  : str
            second : int
        obj = jsxn.example(first='a', second=2)
        self.assertEqual(dict(obj), {'first':'a','second':2})

    def test_slots(self):
        @jsxn
        class example:
            __slots__ = ['first','second']
        self.assertEqual(dict(jsxn.example(first='a')), {'first':'a','second':None})

    def test_single_string_slot(self):
        @jsxn
        class example:
            __slots__ = 'only'
        self.assertEqual(dict(jsxn.example(only=1)), {'only':1})

    def test_methods_are_bound(self):
        @jsxn
        class domain:
            name : str
            def shout(self):
                return self.name.upper()
        self.assertEqual(jsxn.domain(name='www').shout(), 'WWW')

    def test_decorator_returns_generated_class(self):
        @jsxn
        class domain:
            name : str
        self.assertIs(domain, jsxn.domain)

    def test_named(self):
        @jsxn('computer')
        class MachineClass:
            cpu   : str
            cores : int
        obj = jsxn.computer(cpu='x86_64', cores=8)
        self.assertEqual(dict(obj), {'cpu':'x86_64','cores':8})
        self.assertNotIn('MachineClass', _cache)

    def test_called_without_name(self):
        @jsxn()
        class example:
            a : int
        self.assertIn('example', _cache)

    def test_invalid_argument(self):
        with self.assertRaises(TypeError):
            jsxn(42)

    def test_unknown_attribute_rejected(self):
        @jsxn
        class example:
            a : int
        obj = jsxn.example()
        with self.assertRaises(AttributeError):
            obj.not_defined = True
        self.assertFalse(hasattr(obj, '__dict__'))

    def test_class_attributes_kept(self):
        @jsxn
        class example:
            a : int
            LIMIT = 10
        self.assertEqual(jsxn.example().LIMIT, 10)

    def test_merge_into_existing(self):
        @jsxn('host')
        class First:
            addr : str
            def one(self):
                return 1

        @jsxn('host')
        class Second:
            def two(self):
                return 2

        obj = jsxn.host(addr='10.0.0.1')
        self.assertEqual(dict(obj), {'addr':'10.0.0.1'})
        self.assertEqual((obj.one(), obj.two()), (1, 2))
        with self.assertRaises(AttributeError):
            obj.not_defined = True

    def test_merge_with_dynamic(self):
        jsxn.host({'addr':None})

        @jsxn('host')
        class Helpers:
            def ping(self):
                return 'PING ' + self.addr

        self.assertEqual(jsxn.host(addr='1.2.3.4').ping(), 'PING 1.2.3.4')


class TestSubclass(JsxnTestCase):
    def setUp(self):
        super().setUp()

        @jsxn
        class A:
            a : str
            def hello(self):
                return 'hello ' + self.a

        @jsxn
        class B(A):
            b : int

        self.A = A
        self.B = B

    def test_inherited_fields(self):
        obj = jsxn.B(a='x', b=2)
        self.assertEqual(dict(obj), {'a':'x','b':2})
        self.assertEqual(len(obj), 2)

    def test_inherited_fields_default_to_null(self):
        self.assertEqual(dict(jsxn.B()), {'a':None,'b':None})

    def test_inherited_methods(self):
        self.assertEqual(jsxn.B(a='x').hello(), 'hello x')

    def test_unknown_attribute_rejected(self):
        with self.assertRaises(AttributeError):
            jsxn.B().not_defined = True

    def test_base_unchanged(self):
        self.assertEqual(dict(jsxn.A(a='x')), {'a':'x'})

    def test_redeclared_field_not_duplicated(self):
        @jsxn
        class C(self.B):
            a : str
            c : int
        self.assertEqual(list(dict(jsxn.C())), ['a','b','c'])


if __name__ == '__main__':
    unittest.main()
