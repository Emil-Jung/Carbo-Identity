-- Split producer access: capture (producers.office) vs read-only list (producers.view).
-- Remove FSC Public CIS tile permission (public register stays on company websites only).

UPDATE user_permissions
SET permission = 'producers.view'
WHERE permission = 'producers.public.view';

DELETE FROM role_permissions WHERE permission = 'producers.public.view';
