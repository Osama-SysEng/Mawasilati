import 'safety-center_state.dart';

class SafetyCenterController {
  SafetyCenterState state = const SafetyCenterState();
  void beginLoad() => state = const SafetyCenterState(loading: true);
  void fail(String message) => state = SafetyCenterState(error: message);
}
