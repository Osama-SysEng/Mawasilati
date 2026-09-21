import 'booking-flow_state.dart';

class BookingFlowController {
  BookingFlowState state = const BookingFlowState();
  void beginLoad() => state = const BookingFlowState(loading: true);
  void fail(String message) => state = BookingFlowState(error: message);
}
