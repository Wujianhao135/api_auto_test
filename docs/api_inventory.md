# 若依接口清单（自动生成）

> 数据源：http://localhost:8080/v3/api-docs
> 生成时间：脚本运行时，请勿手工编辑；接口变更后重新跑 `parse_openapi.py`
> 接口总数：**151**

## 登录认证（6 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| GET | `/captchaImage` | 获取验证码 | 公开 | - | - |
| GET | `/getInfo` | 获取当前用户信息 | 需Token | - | - |
| GET | `/getRouters` | 获取路由菜单 | 需Token | - | - |
| POST | `/login` | 登录 | 公开 | - | JSON |
| POST | `/register` | 注册 | 公开 | - | JSON |
| POST | `/unlockscreen` | 解锁屏幕 | 需Token | - | JSON |

## 用户管理（18 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| POST | `/system/user` | 新增 | 需Token | - | JSON |
| PUT | `/system/user` | 修改 | 需Token | - | JSON |
| GET | `/system/user/` | 获取当前用户信息 | 需Token | - | - |
| PUT | `/system/user/authRole` | 授权角色 | 需Token | - | - |
| GET | `/system/user/authRole/{userId}` | 查询已授权角色 | 需Token | userId | - |
| PUT | `/system/user/changeStatus` | 修改状态 | 需Token | - | JSON |
| GET | `/system/user/deptTree` | 部门树 | 需Token | - | - |
| POST | `/system/user/export` | 导出 | 需Token | - | - |
| POST | `/system/user/importData` | 导入数据 | 需Token | - | - |
| POST | `/system/user/importTemplate` | 下载导入模板 | 需Token | - | - |
| GET | `/system/user/list` | 列表查询 | 需Token | - | - |
| GET | `/system/user/profile` | 个人信息 | 需Token | - | - |
| PUT | `/system/user/profile` | 修改个人信息 | 需Token | - | JSON |
| POST | `/system/user/profile/avatar` | 上传头像 | 需Token | - | JSON |
| PUT | `/system/user/profile/updatePwd` | 修改密码 | 需Token | - | JSON |
| PUT | `/system/user/resetPwd` | 重置密码 | 需Token | - | JSON |
| DELETE | `/system/user/{userIds}` | 删除 | 需Token | userIds | - |
| GET | `/system/user/{userId}` | 获取当前用户信息 | 需Token | userId | - |

## 角色管理（15 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| POST | `/system/role` | 新增 | 需Token | - | JSON |
| PUT | `/system/role` | 修改 | 需Token | - | JSON |
| GET | `/system/role/authUser/allocatedList` | 已授权用户列表 | 需Token | - | - |
| PUT | `/system/role/authUser/cancel` | 取消授权 | 需Token | - | JSON |
| PUT | `/system/role/authUser/cancelAll` | 批量取消授权 | 需Token | - | - |
| PUT | `/system/role/authUser/selectAll` | 批量授权 | 需Token | - | - |
| GET | `/system/role/authUser/unallocatedList` | 未授权用户列表 | 需Token | - | - |
| PUT | `/system/role/changeStatus` | 修改状态 | 需Token | - | JSON |
| PUT | `/system/role/dataScope` | 分配数据权限 | 需Token | - | JSON |
| GET | `/system/role/deptTree/{roleId}` | 部门树 | 需Token | roleId | - |
| POST | `/system/role/export` | 导出 | 需Token | - | - |
| GET | `/system/role/list` | 列表查询 | 需Token | - | - |
| GET | `/system/role/optionselect` | 下拉选项 | 需Token | - | - |
| DELETE | `/system/role/{roleIds}` | 删除 | 需Token | roleIds | - |
| GET | `/system/role/{roleId}` | 获取当前用户信息 | 需Token | roleId | - |

## 岗位管理（7 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| POST | `/system/post` | 新增 | 需Token | - | JSON |
| PUT | `/system/post` | 修改 | 需Token | - | JSON |
| POST | `/system/post/export` | 导出 | 需Token | - | - |
| GET | `/system/post/list` | 列表查询 | 需Token | - | - |
| GET | `/system/post/optionselect` | 下拉选项 | 需Token | - | - |
| DELETE | `/system/post/{postIds}` | 删除 | 需Token | postIds | - |
| GET | `/system/post/{postId}` | 获取当前用户信息 | 需Token | postId | - |

## 部门管理（7 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| POST | `/system/dept` | 新增 | 需Token | - | JSON |
| PUT | `/system/dept` | 修改 | 需Token | - | JSON |
| GET | `/system/dept/list` | 列表查询 | 需Token | - | - |
| GET | `/system/dept/list/exclude/{deptId}` | 排除指定节点的部门列表 | 需Token | deptId | - |
| PUT | `/system/dept/updateSort` | 修改排序 | 需Token | - | JSON |
| DELETE | `/system/dept/{deptId}` | 删除 | 需Token | deptId | - |
| GET | `/system/dept/{deptId}` | 获取当前用户信息 | 需Token | deptId | - |

## 菜单管理（8 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| POST | `/system/menu` | 新增 | 需Token | - | JSON |
| PUT | `/system/menu` | 修改 | 需Token | - | JSON |
| GET | `/system/menu/list` | 列表查询 | 需Token | - | - |
| GET | `/system/menu/roleMenuTreeselect/{roleId}` | 按角色查菜单树 | 需Token | roleId | - |
| GET | `/system/menu/treeselect` | 树选择 | 需Token | - | - |
| PUT | `/system/menu/updateSort` | 修改排序 | 需Token | - | JSON |
| DELETE | `/system/menu/{menuId}` | 删除 | 需Token | menuId | - |
| GET | `/system/menu/{menuId}` | 获取当前用户信息 | 需Token | menuId | - |

## 字典管理（15 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| POST | `/system/dict/data` | 新增 | 需Token | - | JSON |
| PUT | `/system/dict/data` | 修改 | 需Token | - | JSON |
| POST | `/system/dict/data/export` | 导出 | 需Token | - | - |
| GET | `/system/dict/data/list` | 列表查询 | 需Token | - | - |
| GET | `/system/dict/data/type/{dictType}` | 按类型查字典数据 | 需Token | dictType | - |
| DELETE | `/system/dict/data/{dictCodes}` | 删除 | 需Token | dictCodes | - |
| GET | `/system/dict/data/{dictCode}` | 获取当前用户信息 | 需Token | dictCode | - |
| POST | `/system/dict/type` | 新增 | 需Token | - | JSON |
| PUT | `/system/dict/type` | 修改 | 需Token | - | JSON |
| POST | `/system/dict/type/export` | 导出 | 需Token | - | - |
| GET | `/system/dict/type/list` | 列表查询 | 需Token | - | - |
| GET | `/system/dict/type/optionselect` | 下拉选项 | 需Token | - | - |
| DELETE | `/system/dict/type/refreshCache` | 刷新缓存 | 需Token | - | - |
| DELETE | `/system/dict/type/{dictIds}` | 删除 | 需Token | dictIds | - |
| GET | `/system/dict/type/{dictId}` | 获取当前用户信息 | 需Token | dictId | - |

## 参数配置（8 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| POST | `/system/config` | 新增 | 需Token | - | JSON |
| PUT | `/system/config` | 修改 | 需Token | - | JSON |
| GET | `/system/config/configKey/{configKey}` | 按参数键查询 | 需Token | configKey | - |
| POST | `/system/config/export` | 导出 | 需Token | - | - |
| GET | `/system/config/list` | 列表查询 | 需Token | - | - |
| DELETE | `/system/config/refreshCache` | 刷新缓存 | 需Token | - | - |
| DELETE | `/system/config/{configIds}` | 删除 | 需Token | configIds | - |
| GET | `/system/config/{configId}` | 获取当前用户信息 | 需Token | configId | - |

## 通知公告（9 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| POST | `/system/notice` | 新增 | 需Token | - | JSON |
| PUT | `/system/notice` | 修改 | 需Token | - | JSON |
| GET | `/system/notice/list` | 列表查询 | 需Token | - | - |
| GET | `/system/notice/listTop` | 置顶公告列表 | 需Token | - | - |
| POST | `/system/notice/markRead` | 标记已读 | 需Token | - | - |
| POST | `/system/notice/markReadAll` | 全部已读 | 需Token | - | - |
| GET | `/system/notice/readUsers/list` | 已读用户列表 | 需Token | - | - |
| DELETE | `/system/notice/{noticeIds}` | 删除 | 需Token | noticeIds | - |
| GET | `/system/notice/{noticeId}` | 获取当前用户信息 | 需Token | noticeId | - |

## 监控运维（32 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| GET | `/monitor/cache` | 获取当前用户信息 | 需Token | - | - |
| DELETE | `/monitor/cache/clearCacheAll` | 清空全部缓存 | 需Token | - | - |
| DELETE | `/monitor/cache/clearCacheKey/{cacheKey}` | 按键清缓存 | 需Token | cacheKey | - |
| DELETE | `/monitor/cache/clearCacheName/{cacheName}` | 按名清缓存 | 需Token | cacheName | - |
| GET | `/monitor/cache/getKeys/{cacheName}` | 查缓存键 | 需Token | cacheName | - |
| GET | `/monitor/cache/getNames` | 缓存监控 | 需Token | - | - |
| GET | `/monitor/cache/getValue/{cacheName}/{cacheKey}` | 查缓存值 | 需Token | cacheName, cacheKey | - |
| POST | `/monitor/job` | 新增 | 需Token | - | JSON |
| PUT | `/monitor/job` | 修改 | 需Token | - | JSON |
| PUT | `/monitor/job/changeStatus` | 修改状态 | 需Token | - | JSON |
| POST | `/monitor/job/export` | 导出 | 需Token | - | - |
| GET | `/monitor/job/list` | 列表查询 | 需Token | - | - |
| PUT | `/monitor/job/run` | 执行一次 | 需Token | - | JSON |
| DELETE | `/monitor/job/{jobIds}` | 删除 | 需Token | jobIds | - |
| GET | `/monitor/job/{jobId}` | 获取当前用户信息 | 需Token | jobId | - |
| DELETE | `/monitor/jobLog/clean` | 清空数据 | 需Token | - | - |
| POST | `/monitor/jobLog/export` | 导出 | 需Token | - | - |
| GET | `/monitor/jobLog/list` | 列表查询 | 需Token | - | - |
| DELETE | `/monitor/jobLog/{jobLogIds}` | 删除 | 需Token | jobLogIds | - |
| GET | `/monitor/jobLog/{jobLogId}` | 获取当前用户信息 | 需Token | jobLogId | - |
| DELETE | `/monitor/logininfor/clean` | 清空数据 | 需Token | - | - |
| POST | `/monitor/logininfor/export` | 导出 | 需Token | - | - |
| GET | `/monitor/logininfor/list` | 列表查询 | 需Token | - | - |
| GET | `/monitor/logininfor/unlock/{userName}` | 解锁账号 | 需Token | userName | - |
| DELETE | `/monitor/logininfor/{infoIds}` | 删除 | 需Token | infoIds | - |
| GET | `/monitor/online/list` | 列表查询 | 需Token | - | - |
| DELETE | `/monitor/online/{tokenId}` | 强制退出 | 需Token | tokenId | - |
| DELETE | `/monitor/operlog/clean` | 清空数据 | 需Token | - | - |
| POST | `/monitor/operlog/export` | 导出 | 需Token | - | - |
| GET | `/monitor/operlog/list` | 列表查询 | 需Token | - | - |
| DELETE | `/monitor/operlog/{operIds}` | 删除 | 需Token | operIds | - |
| GET | `/monitor/server` | 获取当前用户信息 | 需Token | - | - |

## 文件上传下载（4 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| GET | `/common/download` | 文件下载 | 需Token | - | - |
| GET | `/common/download/resource` | 资源下载 | 需Token | - | - |
| POST | `/common/upload` | 上传文件 | 需Token | - | - |
| POST | `/common/uploads` | 批量上传 | 需Token | - | - |

## 代码生成（13 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| PUT | `/tool/gen` | 编辑保存 | 需Token | - | JSON |
| GET | `/tool/gen/batchGenCode` | 批量生成 | 需Token | - | - |
| GET | `/tool/gen/column/{tableId}` | 字段列表 | 需Token | tableId | - |
| POST | `/tool/gen/createTable` | 新建表 | 需Token | - | - |
| GET | `/tool/gen/db/list` | 数据库表列表 | 需Token | - | - |
| GET | `/tool/gen/download/{tableName}` | 下载代码 | 需Token | tableName | - |
| GET | `/tool/gen/genCode/{tableName}` | 生成代码 | 需Token | tableName | - |
| POST | `/tool/gen/importTable` | 导入表 | 需Token | - | - |
| GET | `/tool/gen/list` | 生成表列表 | 需Token | - | - |
| GET | `/tool/gen/preview/{tableId}` | 预览代码 | 需Token | tableId | - |
| GET | `/tool/gen/synchDb/{tableName}` | 同步数据库 | 需Token | tableName | - |
| DELETE | `/tool/gen/{tableIds}` | 删除 | 需Token | tableIds | - |
| GET | `/tool/gen/{tableId}` | 获取当前用户信息 | 需Token | tableId | - |

## 其他（9 个）

| 方法 | 路径 | 说明 | 鉴权 | 路径参数 | Body |
|---|---|---|---|---|---|
| DELETE | `/` | index_3 | 需Token | - | - |
| GET | `/` | index | 需Token | - | - |
| POST | `/` | index_1 | 需Token | - | - |
| PUT | `/` | index_2 | 需Token | - | - |
| GET | `/test/user/list` | 获取用户列表 | 需Token | - | - |
| POST | `/test/user/save` | 新增用户 | 需Token | - | - |
| PUT | `/test/user/update` | 更新用户 | 需Token | - | JSON |
| DELETE | `/test/user/{userId}` | 删除用户信息 | 需Token | userId | - |
| GET | `/test/user/{userId}` | 获取用户详细 | 需Token | userId | - |
