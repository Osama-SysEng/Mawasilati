bool canConfirmSafetyCenter(String action, {required bool approved}) {
  const protected = {'payment_capture', 'driver_assignment', 'emergency_escalation'};
  return !protected.contains(action) || approved;
}
