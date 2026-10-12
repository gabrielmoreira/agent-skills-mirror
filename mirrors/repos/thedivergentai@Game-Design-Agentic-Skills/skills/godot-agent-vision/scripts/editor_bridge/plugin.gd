@tool
extends EditorPlugin

## TEMP agent vision bridge — NEVER Autoload, NEVER export.
## Handshake: res://.gdskills/vision/request → raw/*.png → done

const VISION_DIR := "res://.gdskills/vision"
const RAW_DIR := VISION_DIR + "/raw"
const REQUEST := VISION_DIR + "/request"
const DONE := VISION_DIR + "/done"

var _busy: bool = false


func _enter_tree() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(RAW_DIR))


func _exit_tree() -> void:
	_busy = false


func _process(_delta: float) -> void:
	if _busy:
		return
	if not FileAccess.file_exists(REQUEST):
		return
	_busy = true
	_capture_once()


func _capture_once() -> void:
	var mode := "3d"
	var rf := FileAccess.open(REQUEST, FileAccess.READ)
	if rf:
		mode = rf.get_as_text().strip_edges().to_lower()
		rf.close()

	# Remove prior done flag
	if FileAccess.file_exists(DONE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(DONE))

	await RenderingServer.frame_post_draw
	await RenderingServer.frame_post_draw

	var img: Image = null
	match mode:
		"2d":
			EditorInterface.set_main_screen_editor("2D")
			await RenderingServer.frame_post_draw
			var vp2: SubViewport = EditorInterface.get_editor_viewport_2d()
			if vp2:
				img = vp2.get_texture().get_image()
		"main":
			img = await _capture_main_screen()
		_:
			EditorInterface.set_main_screen_editor("3D")
			await RenderingServer.frame_post_draw
			var vp3: SubViewport = EditorInterface.get_editor_viewport_3d(0)
			if vp3:
				img = vp3.get_texture().get_image()

	if img == null or img.is_empty():
		push_error("GDSkills Agent Vision: capture returned empty image")
		_busy = false
		return

	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(RAW_DIR))
	var stamp := Time.get_datetime_string_from_system().replace(":", "").replace(" ", "-")
	var out_path := "%s/capture-%s.png" % [RAW_DIR, stamp]
	var err := img.save_png(out_path)
	if err != OK:
		push_error("GDSkills Agent Vision: save_png failed (%s)" % err)
		_busy = false
		return

	# Write done AFTER png is closed
	var df := FileAccess.open(DONE, FileAccess.WRITE)
	if df:
		df.store_string(out_path + "\n")
		df.close()

	# Clear request so we do not loop
	DirAccess.remove_absolute(ProjectSettings.globalize_path(REQUEST))
	_busy = false


func _capture_main_screen() -> Image:
	var root := get_editor_interface().get_base_control()
	if root == null:
		return null
	await RenderingServer.frame_post_draw
	var vp: Viewport = root.get_viewport()
	if vp == null:
		return null
	return vp.get_texture().get_image()
