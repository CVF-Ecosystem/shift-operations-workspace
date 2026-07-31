# End Shift Report

Operator generate report từ shift đã CLOSED (server tự derive snapshot, không nhận content từ caller); operator submit-review; shift_supervisor approve qua durable R2 receipt (approver phải khác actor duyệt). Freeze chỉ thành công khi có đúng một current report APPROVED và snapshot vẫn khớp truth hiện tại; Report và Shift chuyển FROZEN cùng một transaction với handover readiness. Thay đổi truth sau approve buộc tạo version kế tiếp, không sửa lại bản đã duyệt.
