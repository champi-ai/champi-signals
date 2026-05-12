"""Event processor extracted from Champi services."""

import asyncio
import inspect
import traceback
from contextlib import asynccontextmanager


def _execute_with_events(
    func, service_instance, args, kwargs, data, metadata, is_async
):
    """Execute function with automatic event emission."""

    # Safely extract event configuration
    try:
        event_type = getattr(service_instance.__class__, "Meta", None)
        if event_type and hasattr(event_type, "event_type"):
            event_type = event_type.event_type
        else:
            event_type = "lifecycle"
    except Exception:
        event_type = "lifecycle"

    # Extract signal manager from service metaclass
    signals = None
    try:
        meta = getattr(service_instance.__class__, "Meta", None)
        if meta and hasattr(meta, "signal_manager"):
            signals = meta.signal_manager
        elif meta and hasattr(meta, "signal_manager_class"):
            signals = meta.signal_manager_class()
    except Exception:
        pass

    if signals is None:
        # No signal manager found, skip event emission
        return func(service_instance, *args, **kwargs)

    # Get target signal
    try:
        signal = getattr(signals, event_type)
    except AttributeError:
        # Fallback to lifecycle if event_type not found
        signal = (
            signals.signals.get("lifecycle") if hasattr(signals, "signals") else None
        )

    if signal is None:
        # No valid signal found, skip event emission
        return func(service_instance, *args, **kwargs)

    method_name = func.__name__.upper()
    start_time = None

    # Capture initial variable state
    initial_state = {}
    for var_name in data or []:
        try:
            if var_name.startswith("cls."):
                attr_name = var_name[4:]
                if hasattr(service_instance.__class__, attr_name):
                    initial_state[attr_name] = getattr(
                        service_instance.__class__, attr_name, None
                    )
            else:
                if hasattr(service_instance, var_name):
                    initial_state[var_name] = getattr(service_instance, var_name, None)
        except Exception as e:
            initial_state[f"{var_name}_error"] = f"Failed to capture: {str(e)}"

    # Emit START event
    try:
        if is_async:
            start_time = asyncio.get_event_loop().time()
        start_data = {**initial_state, **metadata, "timestamp": start_time}
        signal.send(
            event_type=event_type,
            sub_event=f"{method_name}_START",
            data=start_data,
        )
    except Exception:
        # Don't break method execution if event emission fails
        pass

    try:
        # Execute original method
        if is_async:
            # This will be awaited by the async wrapper
            result = func(service_instance, *args, **kwargs)
        else:
            result = func(service_instance, *args, **kwargs)

        # Capture final variable state
        final_state = {}
        for var_name in data or []:
            try:
                if var_name.startswith("cls."):
                    attr_name = var_name[4:]
                    if hasattr(service_instance.__class__, attr_name):
                        final_state[attr_name] = getattr(
                            service_instance.__class__, attr_name, None
                        )
                else:
                    if hasattr(service_instance, var_name):
                        final_state[var_name] = getattr(
                            service_instance, var_name, None
                        )
            except Exception as e:
                final_state[f"{var_name}_error"] = f"Failed to capture: {str(e)}"

        # Emit SUCCESS event
        try:
            if is_async:
                end_time = asyncio.get_event_loop().time()
                duration = end_time - start_time if start_time else 0
            else:
                duration = 0
            success_data = {
                **final_state,
                **metadata,
                "success": True,
                "duration_seconds": duration,
            }
            signal.send(
                event_type=event_type,
                sub_event=f"{method_name}_FINISH",
                data=success_data,
            )
        except Exception:
            pass

        return result

    except Exception as ex:
        # Emit ERROR event with full context
        try:
            if is_async:
                end_time = asyncio.get_event_loop().time()
                duration = end_time - start_time if start_time else 0
            else:
                duration = 0
            error_data = {**initial_state, **metadata}
            error_data.update(
                {
                    "error": str(ex),
                    "error_type": type(ex).__name__,
                    "traceback": traceback.format_exc(),
                    "success": False,
                    "duration_seconds": duration,
                }
            )
            signal.send(
                event_type=event_type,
                sub_event=f"{method_name}_ERROR",
                data=error_data,
            )
        except Exception:
            pass

        # Always re-raise the original exception
        raise ex


async def _execute_with_events_async(
    func, service_instance, args, kwargs, data, metadata
):
    """Async version of execute_with_events."""
    # Same logic as above but with await
    result = _execute_with_events(
        func, service_instance, args, kwargs, data, metadata, True
    )
    if asyncio.iscoroutine(result):
        return await result
    return result


class EventProcessor:
    """Event processing decorators for automatic event emission"""

    @staticmethod
    def emits_event(data=None, **metadata):
        """
        Static decorator for START/FINISH/ERROR event emission with state capture

        Args:
            data: List of variable names to track (supports 'cls.var' for class vars)
            **metadata: Additional metadata to include in all events
        """

        def decorator(func):
            if asyncio.iscoroutinefunction(func):

                async def async_wrapper(self, *args, **kwargs):
                    return await _execute_with_events_async(
                        func, self, args, kwargs, data, metadata
                    )

                return async_wrapper
            else:

                def sync_wrapper(self, *args, **kwargs):
                    return _execute_with_events(
                        func, self, args, kwargs, data, metadata, False
                    )

                return sync_wrapper

        return decorator

    @staticmethod
    def periodic_emit(variables=None, interval=3.0):
        """
        Static decorator for continuous variable monitoring during method execution

        Args:
            variables: List of variable names to monitor (supports 'cls.var' for class vars)
            interval: Monitoring interval in seconds
        """

        def decorator(func):
            if not asyncio.iscoroutinefunction(func):
                # Periodic monitoring only works with async functions
                return func

            async def wrapper(self, *args, **kwargs):
                # Safely extract event configuration
                try:
                    event_type = getattr(self.__class__, "Meta", None)
                    if event_type and hasattr(event_type, "event_type"):
                        event_type = event_type.event_type
                    else:
                        event_type = "processing"
                except Exception:
                    event_type = "processing"

                # Extract signal manager from service metaclass
                signals = None
                try:
                    meta = getattr(self.__class__, "Meta", None)
                    if meta and hasattr(meta, "signal_manager"):
                        signals = meta.signal_manager
                    elif meta and hasattr(meta, "signal_manager_class"):
                        signals = meta.signal_manager_class()
                except Exception:
                    pass

                if signals is None:
                    # No signal manager found, skip monitoring
                    return await func(self, *args, **kwargs)

                # Get target signal
                try:
                    signal = getattr(signals, event_type)
                except AttributeError:
                    signal = (
                        signals.signals.get("processing")
                        if hasattr(signals, "signals")
                        else None
                    )

                if signal is None:
                    # No valid signal found, skip monitoring
                    return await func(self, *args, **kwargs)

                method_name = func.__name__.upper()
                monitoring = True
                monitor_task = None

                async def monitor_vars():
                    """Background task for variable monitoring"""
                    last_values = {}

                    while monitoring:
                        try:
                            current_values = {
                                "timestamp": asyncio.get_event_loop().time()
                            }

                            # Capture current variable state
                            for var_name in variables or []:
                                try:
                                    if var_name.startswith("cls."):
                                        attr_name = var_name[4:]
                                        if hasattr(self.__class__, attr_name):
                                            current_values[attr_name] = getattr(
                                                self.__class__, attr_name, None
                                            )
                                    else:
                                        if hasattr(self, var_name):
                                            current_values[var_name] = getattr(
                                                self, var_name, None
                                            )
                                except Exception as e:
                                    current_values[f"{var_name}_error"] = (
                                        f"Monitor error: {str(e)}"
                                    )

                            # Emit if values changed (excluding timestamp)
                            values_without_timestamp = {
                                k: v
                                for k, v in current_values.items()
                                if k != "timestamp"
                            }
                            last_without_timestamp = {
                                k: v for k, v in last_values.items() if k != "timestamp"
                            }

                            if values_without_timestamp != last_without_timestamp:
                                try:
                                    signal.send(
                                        event_type=event_type,
                                        sub_event=f"{method_name}_PROGRESS",
                                        data=current_values,
                                    )
                                except Exception:
                                    pass

                                last_values = current_values.copy()

                            await asyncio.sleep(interval)

                        except asyncio.CancelledError:
                            break
                        except Exception:
                            # Continue monitoring even if individual cycles fail
                            await asyncio.sleep(interval)

                # Start background monitoring
                try:
                    monitor_task = asyncio.create_task(monitor_vars())
                except Exception:
                    monitor_task = None

                try:
                    # Execute original method
                    result = await func(self, *args, **kwargs)
                    return result

                finally:
                    # Clean up monitoring
                    monitoring = False
                    if monitor_task and not monitor_task.done():
                        monitor_task.cancel()
                        try:
                            await monitor_task
                        except (asyncio.CancelledError, Exception):
                            pass

            return wrapper

        return decorator

    @classmethod
    def emits_all_events(cls, data=None):
        """
        Class decorator that applies ``emits_event`` to every public, non-dunder
        method on the decorated class, excluding any inner ``Meta`` class.

        Args:
            data: List of variable names to track, forwarded to each ``emits_event``
                call (supports ``'cls.var'`` for class-level attributes).

        Returns:
            A class decorator that wraps all eligible methods with event emission.

        Example::

            @EventProcessor.emits_all_events(data=["status"])
            class MyService:
                class Meta:
                    event_type = "processing"
                    signal_manager = my_signals
        """

        def decorator(klass):
            for name, method in inspect.getmembers(klass, predicate=inspect.isfunction):
                if name.startswith("_"):
                    continue
                if name == "Meta":
                    continue
                wrapped = cls.emits_event(data=data)(method)
                setattr(klass, name, wrapped)
            return klass

        return decorator

    @staticmethod
    @asynccontextmanager
    async def context(signal_manager, event_type, data=None):
        """
        Async context manager that emits lifecycle events around a code block.

        Emits ``<event_type>_START`` on entry, ``<event_type>_FINISH`` on clean
        exit, and ``<event_type>_ERROR`` (then re-raises) if an exception
        propagates.

        Args:
            signal_manager: A signal manager instance whose attribute named
                ``event_type`` is a signal accepting ``send(event_type=...,
                sub_event=..., data=...)``.
            event_type: String key used to look up the signal on
                ``signal_manager`` and as the ``event_type`` value in emitted
                events.
            data: Optional dict of arbitrary data included in every emitted event.

        Raises:
            Exception: Any exception raised inside the ``async with`` block is
                re-raised after the ``<event_type>_ERROR`` event is emitted.

        Example::

            async with EventProcessor.context(signals, "processing", data={"job": 1}):
                await do_work()
        """
        try:
            signal = getattr(signal_manager, event_type)
        except AttributeError:
            signal = None

        event_data = dict(data or {})

        if signal is not None:
            try:
                signal.send(
                    event_type=event_type,
                    sub_event=f"{event_type.upper()}_START",
                    data=event_data,
                )
            except Exception:
                pass

        try:
            yield
        except Exception as ex:
            if signal is not None:
                try:
                    signal.send(
                        event_type=event_type,
                        sub_event=f"{event_type.upper()}_ERROR",
                        data={
                            **event_data,
                            "error": str(ex),
                            "error_type": type(ex).__name__,
                        },
                    )
                except Exception:
                    pass
            raise
        else:
            if signal is not None:
                try:
                    signal.send(
                        event_type=event_type,
                        sub_event=f"{event_type.upper()}_FINISH",
                        data=event_data,
                    )
                except Exception:
                    pass
