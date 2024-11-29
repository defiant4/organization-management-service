"""
pulled from: https://gist.github.com/ddanier/ead419826ac6c3d75c96f9d89bea9bd0
This allows to use global variables inside the FastAPI application
using async mode.
# Usage
Just import `g` and then access (set/get) attributes of it:
```python
from your_project.globals import g
g.foo = "foo"
# In some other code
assert g.foo == "foo"
```
Best way to utilize the global `g` in your code is to set the desired
value in a FastAPI dependency, like so:
```python
async def set_global_foo() -> None:
    g.foo = "foo"
@app.get("/test/", dependencies=[Depends(set_global_foo)])
async def test():
    assert g.foo == "foo"
```
# Setup
Add the `GlobalsMiddleware` to your app:
```python
app = fastapi.FastAPI(
    title="Your app API",
)
app.add_middleware(GlobalsMiddleware)  # <-- This line is necessary
```
Then just use it. ;-)
"""
import logging
from contextvars import Context
from contextvars import ContextVar
from contextvars import Token
from contextvars import copy_context
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import TypeVar
from typing import Union

_T = TypeVar("_T")
logger = logging.getLogger(__name__)


class ContextVarManager:
    __slots__ = ("_vars", "_reset_tokens", "_context_logical_namespace", "_default_values_for_vars")

    _vars: Dict[str, ContextVar]
    _reset_tokens: Dict[str, Token]
    _context_logical_namespace: str
    _default_values_for_vars: Dict[str, _T]

    def __init__(self, namespace: Optional[str] = None, pre_defined_attrs: List[Union[str, Tuple[str, _T]]] = []) -> None:
        """
        The class attribute _vars: Stores a dict which manages individual contextVars
        _reset_tokens: Stores the last reset token for a given contextVar the class is managing in _vars
        _namesapce: An optional logical namespace we want the class to attach to contextVars

        :param namespace: An optional logical namespace we want the class to attach to contextVars
        :param pre_defined_attrs: An Optional list of string contexVar names or 2 Tuples of string contextVar and its default value
        """
        object.__setattr__(self, "_vars", {})
        object.__setattr__(self, "_reset_tokens", {})
        object.__setattr__(self, "_default_values_for_vars", {})
        if namespace and isinstance(namespace, str):
            object.__setattr__(self, "_context_logical_namespace", namespace)
        else:
            object.__setattr__(self, "_context_logical_namespace", "globals")

        if pre_defined_attrs:
            self._mk_pre_defined_attrs_as_contextvars(pre_defined_attrs=pre_defined_attrs)

    def _mk_pre_defined_attrs_as_contextvars(self, pre_defined_attrs: List[Union[str, Tuple[str, _T]]]) -> None:
        str_attrs: List[str] = list(filter(lambda x: isinstance(x, str), pre_defined_attrs))
        default_value_attrs: List[Tuple[str, _T]] = list(filter(lambda x: isinstance(x, tuple) or isinstance(x, Tuple), pre_defined_attrs))

        # create context vars with none as defaults
        for item_name in str_attrs:
            eval_item_name = f"{self._context_logical_namespace}:{item_name}"
            if eval_item_name in self._vars:
                # var already exists so skip recreating it
                logger.info(f"The contextVar with the name: {item_name} already exists in namespace: {self._context_logical_namespace}")
                continue
            # var does not already exist
            self._vars[eval_item_name] = ContextVar(eval_item_name, default=None)
            self._reset_tokens[eval_item_name] = self._vars[eval_item_name].set(None)

        # create context vars with default values
        for item in default_value_attrs:
            if len(item) != 2:
                # skip an incorrectly provided contextVar
                logger.warn(f"The contextVar with the default has too many values. Expected: 2 got: {len(item)}")
                continue

            eval_item_name = f"{self._context_logical_namespace}:{item[0]}"
            item_default = item[1]
            if eval_item_name in self._vars:
                # var already exists so skip recreating it
                logger.info(f"The contextVar with the name: {item[0]} already exists in namespace: {self._context_logical_namespace}")
                continue
            # var does not already exist
            self._vars[eval_item_name] = ContextVar(eval_item_name, default=item_default() if callable(item_default) else item_default)
            if callable(item_default):
                self._reset_tokens[eval_item_name] = self._vars[eval_item_name].set(item_default())
            else:
                self._reset_tokens[eval_item_name] = self._vars[eval_item_name].set(item_default)

            self._default_values_for_vars[eval_item_name] = item_default

    def reset(self) -> None:
        for _name, var in self._vars.items():
            try:
                var.reset(self._reset_tokens[_name])
            # ValueError will be thrown if the reset() happens in
            # a different context compared to the original set().
            # Then just set to None for this new context.
            except ValueError:
                default_val = self._default_values_for_vars.get(_name, None)
                if callable(default_val):
                    var.set(default_val())
                else:
                    var.set(default_val)

    def _ensure_var(self, item: str) -> None:
        if item not in self._vars:
            self._vars[item] = ContextVar(item, default=None)
            self._reset_tokens[item] = self._vars[item].set(None)

    def __getattr__(self, item: str) -> Any:
        eval_item_name = item
        if not eval_item_name.startswith(self._context_logical_namespace):
            eval_item_name = f"{self._context_logical_namespace}:{eval_item_name}"

        self._ensure_var(eval_item_name)
        return self._vars[eval_item_name].get()

    def __setattr__(self, item: str, value: Any) -> None:
        eval_item_name = item
        if not eval_item_name.startswith(self._context_logical_namespace):
            eval_item_name = f"{self._context_logical_namespace}:{eval_item_name}"

        self._ensure_var(eval_item_name)
        self._reset_tokens[eval_item_name] = self._vars[eval_item_name].set(value)


def get_contextvar_context_by_name(contextvar_name: str, namespace: str = "globals", ignore_namespace: bool = False) -> Union[ContextVar, RuntimeError]:
    cur_context: Context = copy_context()
    if ignore_namespace:
        ctx = list(filter(lambda ctx: ctx.name == f"{contextvar_name}", iter(cur_context)))
    else:
        ctx = list(filter(lambda ctx: ctx.name == f"{namespace}:{contextvar_name}", iter(cur_context)))

    if len(ctx) != 1:
        if ignore_namespace:
            raise RuntimeError(f"ContextVar: {contextvar_name} not found")
        raise RuntimeError(f"ContextVar: {namespace}:{contextvar_name} not found")

    return ctx[0]


def get_contextvar_value_by_name(contextvar_name: str, namespace: str = "globals", ignore_namespace: bool = False) -> Any:
    ctx: ContextVar = get_contextvar_context_by_name(namespace=namespace, contextvar_name=contextvar_name, ignore_namespace=ignore_namespace)
    return ctx.get()


def get_contextvar_context_by_names(
    contextvar_name_list: List[str], namespace: str = "globals", ignore_namespace: bool = False
) -> List[Union[ContextVar, RuntimeError]]:
    current_ctx: Context = copy_context()
    ctx_name_map: Dict[str, ContextVar] = {ctx.name: ctx for ctx in iter(current_ctx)}
    result: List[Union[ContextVar, RuntimeError]] = []
    for contextvar_name in contextvar_name_list:
        if ignore_namespace:
            result.append(ctx_name_map.get(contextvar_name, RuntimeError(f"ContextVar: {contextvar_name} not found")))
        else:
            result.append(ctx_name_map.get(f"{namespace}:{contextvar_name}", RuntimeError(f"ContextVar: {namespace}:{contextvar_name} not found")))

    return result


g = ContextVarManager()
