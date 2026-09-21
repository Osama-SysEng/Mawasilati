import 'driver-console_state.dart';

class DriverConsoleController {
  DriverConsoleState state = const DriverConsoleState();
  void beginLoad() => state = const DriverConsoleState(loading: true);
  void fail(String message) => state = DriverConsoleState(error: message);
}
