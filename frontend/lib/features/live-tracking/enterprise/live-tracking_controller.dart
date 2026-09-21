import 'live-tracking_state.dart';

class LiveTrackingController {
  LiveTrackingState state = const LiveTrackingState();
  void beginLoad() => state = const LiveTrackingState(loading: true);
  void fail(String message) => state = LiveTrackingState(error: message);
}
