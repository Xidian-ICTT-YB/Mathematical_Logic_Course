; ModuleID = './built-in.bc'
source_filename = "llvm-link"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%struct.platform_device = type { %struct.device }
%struct.device = type { i32 }
%struct.of_device_id = type { i8* }
%struct.acpi_device_id = type { [16 x i8], i64 }
%struct.xgene_ahci_context = type { %struct.ahci_host_priv*, %struct.device*, [2 x i8], [2 x i32], i8*, i8*, i8*, i8* }
%struct.ahci_host_priv = type { i8*, i8*, i32, i32 (i32, i8*)* }
%struct.acpi_device_info = type { i32, i32 }

@llvm.used = appending global [2 x i8*] [i8* bitcast (i32 (i32)* @history_entry to i8*), i8* bitcast (i32 (i32)* @history_entry_failure to i8*)], section "llvm.metadata"
@stub_acpi_handle = internal global i64 0, align 8, !dbg !0
@global_pdev = internal global %struct.platform_device zeroinitializer, align 4, !dbg !17
@xgene_ahci_probe.ppi = private unnamed_addr constant [2 x %struct.device*] [%struct.device* @xgene_ahci_v1_port_info, %struct.device* @xgene_ahci_v2_port_info], align 16
@xgene_ahci_of_match = internal constant [1 x %struct.of_device_id] zeroinitializer, align 8, !dbg !75
@xgene_ahci_acpi_match = internal constant [3 x %struct.acpi_device_id] [%struct.acpi_device_id { [16 x i8] c"APMC0D0D\00\00\00\00\00\00\00\00", i64 1 }, %struct.acpi_device_id { [16 x i8] c"APMC0D32\00\00\00\00\00\00\00\00", i64 2 }, %struct.acpi_device_id zeroinitializer], align 16, !dbg !96
@.str = private unnamed_addr constant [46 x i8] c"No node entry in ACPI table. Assume version1\0A\00", align 1
@.str.1 = private unnamed_addr constant [48 x i8] c"%s: Error reading device info. Assume version1\0A\00", align 1
@__func__.xgene_ahci_probe = private unnamed_addr constant [17 x i8] c"xgene_ahci_probe\00", align 1
@.str.2 = private unnamed_addr constant [28 x i8] c"VAddr 0x%p Mmio VAddr 0x%p\0A\00", align 1
@.str.3 = private unnamed_addr constant [36 x i8] c"SATA mux selection failed error %d\0A\00", align 1
@.str.4 = private unnamed_addr constant [35 x i8] c"skip clock and PHY initialization\0A\00", align 1
@ahci_platform_sht = internal global %struct.device zeroinitializer, align 4, !dbg !102
@.str.5 = private unnamed_addr constant [41 x i8] c"X-Gene SATA host controller initialized\0A\00", align 1
@global_acpi_id = internal global %struct.acpi_device_id { [16 x i8] c"APMC0D32\00\00\00\00\00\00\00\00", i64 2 }, align 8, !dbg !86
@global_resource = internal global %struct.device zeroinitializer, align 4, !dbg !70
@global_ctx = internal global %struct.xgene_ahci_context zeroinitializer, align 8, !dbg !46
@global_hpriv = internal global %struct.ahci_host_priv zeroinitializer, align 8, !dbg !34
@xgene_ahci_v1_port_info = internal constant %struct.device { i32 1 }, align 4, !dbg !26
@xgene_ahci_v2_port_info = internal constant %struct.device { i32 2 }, align 4, !dbg !32

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @history_entry(i32) #0 !dbg !115 {
ahci_xgene_h2.llbc-history_entry-0:
  %1 = alloca i32, align 4
  store i32 %0, i32* %1, align 4
  %2 = load i32, i32* %1, align 4, !dbg !119
  %3 = sext i32 %2 to i64, !dbg !120
  store volatile i64 %3, i64* @stub_acpi_handle, align 8, !dbg !121
  %4 = call i32 @xgene_ahci_probe(%struct.platform_device* @global_pdev), !dbg !122
  ret i32 %4, !dbg !123
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @history_entry_failure(i32) #0 !dbg !124 {
ahci_xgene_h2.llbc-history_entry_failure-0:
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  store i32 %0, i32* %2, align 4
  %3 = load i32, i32* %2, align 4, !dbg !125
  %4 = icmp ne i32 %3, 0, !dbg !127
  br i1 %4, label %ahci_xgene_h2.llbc-history_entry_failure-1, label %ahci_xgene_h2.llbc-history_entry_failure-2, !dbg !128

ahci_xgene_h2.llbc-history_entry_failure-1:       ; preds = %ahci_xgene_h2.llbc-history_entry_failure-0
  store i32 0, i32* %1, align 4, !dbg !129
  br label %ahci_xgene_h2.llbc-history_entry_failure-3, !dbg !129

ahci_xgene_h2.llbc-history_entry_failure-2:       ; preds = %ahci_xgene_h2.llbc-history_entry_failure-0
  store volatile i64 0, i64* @stub_acpi_handle, align 8, !dbg !130
  %5 = call i32 @xgene_ahci_probe(%struct.platform_device* @global_pdev), !dbg !131
  store i32 %5, i32* %1, align 4, !dbg !132
  br label %ahci_xgene_h2.llbc-history_entry_failure-3, !dbg !132

ahci_xgene_h2.llbc-history_entry_failure-3:       ; preds = %ahci_xgene_h2.llbc-history_entry_failure-2, %ahci_xgene_h2.llbc-history_entry_failure-1
  %6 = load i32, i32* %1, align 4, !dbg !133
  ret i32 %6, !dbg !133
}

; Function Attrs: nounwind readnone speculatable
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @xgene_ahci_probe(%struct.platform_device*) #0 !dbg !134 {
ahci_xgene_h2.llbc-xgene_ahci_probe-0:
  %1 = alloca i32, align 4
  %2 = alloca %struct.platform_device*, align 8
  %3 = alloca %struct.device*, align 8
  %4 = alloca %struct.ahci_host_priv*, align 8
  %5 = alloca %struct.xgene_ahci_context*, align 8
  %6 = alloca %struct.device*, align 8
  %7 = alloca %struct.of_device_id*, align 8
  %8 = alloca i32, align 4
  %9 = alloca [2 x %struct.device*], align 16
  %10 = alloca i32, align 4
  %11 = alloca i8*, align 8
  %12 = alloca %struct.acpi_device_id*, align 8
  %13 = alloca %struct.acpi_device_info*, align 8
  %14 = alloca i32, align 4
  store %struct.platform_device* %0, %struct.platform_device** %2, align 8
  %15 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !139
  %16 = getelementptr inbounds %struct.platform_device, %struct.platform_device* %15, i32 0, i32 0, !dbg !140
  store %struct.device* %16, %struct.device** %3, align 8, !dbg !141
  store i32 1, i32* %8, align 4, !dbg !142
  %17 = bitcast [2 x %struct.device*]* %9 to i8*, !dbg !143
  %18 = call i8* @memcpy(i8* %17, i8* bitcast ([2 x %struct.device*]* @xgene_ahci_probe.ppi to i8*), i64 16), !dbg !143
  %19 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !144
  %20 = call %struct.ahci_host_priv* @ahci_platform_get_resources(%struct.platform_device* %19), !dbg !145
  store %struct.ahci_host_priv* %20, %struct.ahci_host_priv** %4, align 8, !dbg !146
  %21 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !147
  %22 = ptrtoint %struct.ahci_host_priv* %21 to i64, !dbg !147
  %23 = icmp uge i64 %22, -4095, !dbg !147
  br i1 %23, label %ahci_xgene_h2.llbc-xgene_ahci_probe-1, label %ahci_xgene_h2.llbc-xgene_ahci_probe-2, !dbg !149

ahci_xgene_h2.llbc-xgene_ahci_probe-1:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-0
  %24 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !150
  %25 = ptrtoint %struct.ahci_host_priv* %24 to i64, !dbg !150
  %26 = trunc i64 %25 to i32, !dbg !150
  store i32 %26, i32* %1, align 4, !dbg !151
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !151

ahci_xgene_h2.llbc-xgene_ahci_probe-2:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-0
  %27 = load %struct.device*, %struct.device** %3, align 8, !dbg !152
  %28 = call i8* @devm_kzalloc(%struct.device* %27, i64 64, i32 0), !dbg !153
  %29 = bitcast i8* %28 to %struct.xgene_ahci_context*, !dbg !153
  store %struct.xgene_ahci_context* %29, %struct.xgene_ahci_context** %5, align 8, !dbg !154
  %30 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !155
  %31 = icmp ne %struct.xgene_ahci_context* %30, null, !dbg !155
  br i1 %31, label %ahci_xgene_h2.llbc-xgene_ahci_probe-4, label %ahci_xgene_h2.llbc-xgene_ahci_probe-3, !dbg !157

ahci_xgene_h2.llbc-xgene_ahci_probe-3:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-2
  store i32 -12, i32* %1, align 4, !dbg !158
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !158

ahci_xgene_h2.llbc-xgene_ahci_probe-4:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-2
  %32 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !159
  %33 = bitcast %struct.xgene_ahci_context* %32 to i8*, !dbg !159
  %34 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !160
  %35 = getelementptr inbounds %struct.ahci_host_priv, %struct.ahci_host_priv* %34, i32 0, i32 1, !dbg !161
  store i8* %33, i8** %35, align 8, !dbg !162
  %36 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !163
  %37 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !164
  %38 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %37, i32 0, i32 0, !dbg !165
  store %struct.ahci_host_priv* %36, %struct.ahci_host_priv** %38, align 8, !dbg !166
  %39 = load %struct.device*, %struct.device** %3, align 8, !dbg !167
  %40 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !168
  %41 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %40, i32 0, i32 1, !dbg !169
  store %struct.device* %39, %struct.device** %41, align 8, !dbg !170
  %42 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !171
  %43 = call %struct.device* @platform_get_resource(%struct.platform_device* %42, i32 512, i32 1), !dbg !172
  store %struct.device* %43, %struct.device** %6, align 8, !dbg !173
  %44 = load %struct.device*, %struct.device** %3, align 8, !dbg !174
  %45 = load %struct.device*, %struct.device** %6, align 8, !dbg !175
  %46 = call i8* @devm_ioremap_resource(%struct.device* %44, %struct.device* %45), !dbg !176
  %47 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !177
  %48 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %47, i32 0, i32 4, !dbg !178
  store i8* %46, i8** %48, align 8, !dbg !179
  %49 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !180
  %50 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %49, i32 0, i32 4, !dbg !180
  %51 = load i8*, i8** %50, align 8, !dbg !180
  %52 = ptrtoint i8* %51 to i64, !dbg !180
  %53 = icmp uge i64 %52, -4095, !dbg !180
  br i1 %53, label %ahci_xgene_h2.llbc-xgene_ahci_probe-5, label %ahci_xgene_h2.llbc-xgene_ahci_probe-6, !dbg !182

ahci_xgene_h2.llbc-xgene_ahci_probe-5:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-4
  %54 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !183
  %55 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %54, i32 0, i32 4, !dbg !183
  %56 = load i8*, i8** %55, align 8, !dbg !183
  %57 = ptrtoint i8* %56 to i64, !dbg !183
  %58 = trunc i64 %57 to i32, !dbg !183
  store i32 %58, i32* %1, align 4, !dbg !184
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !184

ahci_xgene_h2.llbc-xgene_ahci_probe-6:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-4
  %59 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !185
  %60 = call %struct.device* @platform_get_resource(%struct.platform_device* %59, i32 512, i32 2), !dbg !186
  store %struct.device* %60, %struct.device** %6, align 8, !dbg !187
  %61 = load %struct.device*, %struct.device** %3, align 8, !dbg !188
  %62 = load %struct.device*, %struct.device** %6, align 8, !dbg !189
  %63 = call i8* @devm_ioremap_resource(%struct.device* %61, %struct.device* %62), !dbg !190
  %64 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !191
  %65 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %64, i32 0, i32 5, !dbg !192
  store i8* %63, i8** %65, align 8, !dbg !193
  %66 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !194
  %67 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %66, i32 0, i32 5, !dbg !194
  %68 = load i8*, i8** %67, align 8, !dbg !194
  %69 = ptrtoint i8* %68 to i64, !dbg !194
  %70 = icmp uge i64 %69, -4095, !dbg !194
  br i1 %70, label %ahci_xgene_h2.llbc-xgene_ahci_probe-7, label %ahci_xgene_h2.llbc-xgene_ahci_probe-8, !dbg !196

ahci_xgene_h2.llbc-xgene_ahci_probe-7:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-6
  %71 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !197
  %72 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %71, i32 0, i32 5, !dbg !197
  %73 = load i8*, i8** %72, align 8, !dbg !197
  %74 = ptrtoint i8* %73 to i64, !dbg !197
  %75 = trunc i64 %74 to i32, !dbg !197
  store i32 %75, i32* %1, align 4, !dbg !198
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !198

ahci_xgene_h2.llbc-xgene_ahci_probe-8:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-6
  %76 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !199
  %77 = call %struct.device* @platform_get_resource(%struct.platform_device* %76, i32 512, i32 3), !dbg !200
  store %struct.device* %77, %struct.device** %6, align 8, !dbg !201
  %78 = load %struct.device*, %struct.device** %3, align 8, !dbg !202
  %79 = load %struct.device*, %struct.device** %6, align 8, !dbg !203
  %80 = call i8* @devm_ioremap_resource(%struct.device* %78, %struct.device* %79), !dbg !204
  %81 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !205
  %82 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %81, i32 0, i32 6, !dbg !206
  store i8* %80, i8** %82, align 8, !dbg !207
  %83 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !208
  %84 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %83, i32 0, i32 6, !dbg !208
  %85 = load i8*, i8** %84, align 8, !dbg !208
  %86 = ptrtoint i8* %85 to i64, !dbg !208
  %87 = icmp uge i64 %86, -4095, !dbg !208
  br i1 %87, label %ahci_xgene_h2.llbc-xgene_ahci_probe-9, label %ahci_xgene_h2.llbc-xgene_ahci_probe-10, !dbg !210

ahci_xgene_h2.llbc-xgene_ahci_probe-9:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-8
  %88 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !211
  %89 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %88, i32 0, i32 6, !dbg !211
  %90 = load i8*, i8** %89, align 8, !dbg !211
  %91 = ptrtoint i8* %90 to i64, !dbg !211
  %92 = trunc i64 %91 to i32, !dbg !211
  store i32 %92, i32* %1, align 4, !dbg !212
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !212

ahci_xgene_h2.llbc-xgene_ahci_probe-10:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-8
  %93 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !213
  %94 = call %struct.device* @platform_get_resource(%struct.platform_device* %93, i32 512, i32 4), !dbg !214
  store %struct.device* %94, %struct.device** %6, align 8, !dbg !215
  %95 = load %struct.device*, %struct.device** %6, align 8, !dbg !216
  %96 = icmp ne %struct.device* %95, null, !dbg !216
  br i1 %96, label %ahci_xgene_h2.llbc-xgene_ahci_probe-11, label %ahci_xgene_h2.llbc-xgene_ahci_probe-14, !dbg !218

ahci_xgene_h2.llbc-xgene_ahci_probe-11:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-10
  %97 = load %struct.device*, %struct.device** %3, align 8, !dbg !219
  %98 = load %struct.device*, %struct.device** %6, align 8, !dbg !221
  %99 = call i8* @devm_ioremap_resource(%struct.device* %97, %struct.device* %98), !dbg !222
  store i8* %99, i8** %11, align 8, !dbg !223
  %100 = load i8*, i8** %11, align 8, !dbg !224
  %101 = ptrtoint i8* %100 to i64, !dbg !224
  %102 = icmp uge i64 %101, -4095, !dbg !224
  br i1 %102, label %ahci_xgene_h2.llbc-xgene_ahci_probe-12, label %ahci_xgene_h2.llbc-xgene_ahci_probe-13, !dbg !226

ahci_xgene_h2.llbc-xgene_ahci_probe-12:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-11
  %103 = load i8*, i8** %11, align 8, !dbg !227
  %104 = ptrtoint i8* %103 to i64, !dbg !227
  %105 = trunc i64 %104 to i32, !dbg !227
  store i32 %105, i32* %1, align 4, !dbg !228
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !228

ahci_xgene_h2.llbc-xgene_ahci_probe-13:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-11
  %106 = load i8*, i8** %11, align 8, !dbg !229
  %107 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !230
  %108 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %107, i32 0, i32 7, !dbg !231
  store i8* %106, i8** %108, align 8, !dbg !232
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-14, !dbg !233

ahci_xgene_h2.llbc-xgene_ahci_probe-14:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-13, %ahci_xgene_h2.llbc-xgene_ahci_probe-10
  %109 = load %struct.device*, %struct.device** %3, align 8, !dbg !234
  %110 = call %struct.of_device_id* @of_match_device(%struct.of_device_id* getelementptr inbounds ([1 x %struct.of_device_id], [1 x %struct.of_device_id]* @xgene_ahci_of_match, i32 0, i32 0), %struct.device* %109), !dbg !235
  store %struct.of_device_id* %110, %struct.of_device_id** %7, align 8, !dbg !236
  %111 = load %struct.of_device_id*, %struct.of_device_id** %7, align 8, !dbg !237
  %112 = icmp ne %struct.of_device_id* %111, null, !dbg !237
  br i1 %112, label %ahci_xgene_h2.llbc-xgene_ahci_probe-15, label %ahci_xgene_h2.llbc-xgene_ahci_probe-18, !dbg !239

ahci_xgene_h2.llbc-xgene_ahci_probe-15:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-14
  %113 = load %struct.of_device_id*, %struct.of_device_id** %7, align 8, !dbg !240
  %114 = getelementptr inbounds %struct.of_device_id, %struct.of_device_id* %113, i32 0, i32 0, !dbg !243
  %115 = load i8*, i8** %114, align 8, !dbg !243
  %116 = icmp ne i8* %115, null, !dbg !240
  br i1 %116, label %ahci_xgene_h2.llbc-xgene_ahci_probe-16, label %ahci_xgene_h2.llbc-xgene_ahci_probe-17, !dbg !244

ahci_xgene_h2.llbc-xgene_ahci_probe-16:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-15
  %117 = load %struct.of_device_id*, %struct.of_device_id** %7, align 8, !dbg !245
  %118 = getelementptr inbounds %struct.of_device_id, %struct.of_device_id* %117, i32 0, i32 0, !dbg !246
  %119 = load i8*, i8** %118, align 8, !dbg !246
  %120 = ptrtoint i8* %119 to i32, !dbg !247
  store i32 %120, i32* %8, align 4, !dbg !248
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-17, !dbg !249

ahci_xgene_h2.llbc-xgene_ahci_probe-17:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-16, %ahci_xgene_h2.llbc-xgene_ahci_probe-15
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-29, !dbg !250

ahci_xgene_h2.llbc-xgene_ahci_probe-18:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-14
  %121 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !251
  %122 = getelementptr inbounds %struct.platform_device, %struct.platform_device* %121, i32 0, i32 0, !dbg !253
  %123 = call %struct.acpi_device_id* @acpi_match_device(%struct.acpi_device_id* getelementptr inbounds ([3 x %struct.acpi_device_id], [3 x %struct.acpi_device_id]* @xgene_ahci_acpi_match, i32 0, i32 0), %struct.device* %122), !dbg !254
  store %struct.acpi_device_id* %123, %struct.acpi_device_id** %12, align 8, !dbg !255
  %124 = load %struct.acpi_device_id*, %struct.acpi_device_id** %12, align 8, !dbg !256
  %125 = icmp ne %struct.acpi_device_id* %124, null, !dbg !256
  br i1 %125, label %ahci_xgene_h2.llbc-xgene_ahci_probe-20, label %ahci_xgene_h2.llbc-xgene_ahci_probe-19, !dbg !258

ahci_xgene_h2.llbc-xgene_ahci_probe-19:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-18
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([46 x i8], [46 x i8]* @.str, i32 0, i32 0)), !dbg !259
  store i32 1, i32* %8, align 4, !dbg !261
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-28, !dbg !262

ahci_xgene_h2.llbc-xgene_ahci_probe-20:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-18
  %126 = load %struct.acpi_device_id*, %struct.acpi_device_id** %12, align 8, !dbg !263
  %127 = getelementptr inbounds %struct.acpi_device_id, %struct.acpi_device_id* %126, i32 0, i32 1, !dbg !265
  %128 = load i64, i64* %127, align 8, !dbg !265
  %129 = icmp ne i64 %128, 0, !dbg !263
  br i1 %129, label %ahci_xgene_h2.llbc-xgene_ahci_probe-21, label %ahci_xgene_h2.llbc-xgene_ahci_probe-27, !dbg !266

ahci_xgene_h2.llbc-xgene_ahci_probe-21:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-20
  %130 = load %struct.acpi_device_id*, %struct.acpi_device_id** %12, align 8, !dbg !267
  %131 = getelementptr inbounds %struct.acpi_device_id, %struct.acpi_device_id* %130, i32 0, i32 1, !dbg !269
  %132 = load i64, i64* %131, align 8, !dbg !269
  %133 = trunc i64 %132 to i32, !dbg !270
  store i32 %133, i32* %8, align 4, !dbg !271
  %134 = load volatile i64, i64* @stub_acpi_handle, align 8, !dbg !272
  %135 = call i32 @acpi_get_object_info(i64 %134, %struct.acpi_device_info** %13), !dbg !273
  store i32 %135, i32* %14, align 4, !dbg !274
  %136 = load i32, i32* %14, align 4, !dbg !275
  %137 = icmp ne i32 %136, 0, !dbg !275
  br i1 %137, label %ahci_xgene_h2.llbc-xgene_ahci_probe-22, label %ahci_xgene_h2.llbc-xgene_ahci_probe-23, !dbg !277

ahci_xgene_h2.llbc-xgene_ahci_probe-22:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-21
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([48 x i8], [48 x i8]* @.str.1, i32 0, i32 0), i8* getelementptr inbounds ([17 x i8], [17 x i8]* @__func__.xgene_ahci_probe, i32 0, i32 0)), !dbg !278
  store i32 1, i32* %8, align 4, !dbg !280
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-26, !dbg !281

ahci_xgene_h2.llbc-xgene_ahci_probe-23:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-21
  %138 = load %struct.acpi_device_info*, %struct.acpi_device_info** %13, align 8, !dbg !282
  %139 = getelementptr inbounds %struct.acpi_device_info, %struct.acpi_device_info* %138, i32 0, i32 0, !dbg !284
  %140 = load i32, i32* %139, align 4, !dbg !284
  %141 = and i32 %140, 1, !dbg !285
  %142 = icmp ne i32 %141, 0, !dbg !285
  br i1 %142, label %ahci_xgene_h2.llbc-xgene_ahci_probe-24, label %ahci_xgene_h2.llbc-xgene_ahci_probe-25, !dbg !286

ahci_xgene_h2.llbc-xgene_ahci_probe-24:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-23
  store i32 2, i32* %8, align 4, !dbg !287
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-25, !dbg !289

ahci_xgene_h2.llbc-xgene_ahci_probe-25:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-24, %ahci_xgene_h2.llbc-xgene_ahci_probe-23
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-26

ahci_xgene_h2.llbc-xgene_ahci_probe-26:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-25, %ahci_xgene_h2.llbc-xgene_ahci_probe-22
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-27, !dbg !290

ahci_xgene_h2.llbc-xgene_ahci_probe-27:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-26, %ahci_xgene_h2.llbc-xgene_ahci_probe-20
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-28

ahci_xgene_h2.llbc-xgene_ahci_probe-28:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-27, %ahci_xgene_h2.llbc-xgene_ahci_probe-19
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-29

ahci_xgene_h2.llbc-xgene_ahci_probe-29:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-28, %ahci_xgene_h2.llbc-xgene_ahci_probe-17
  %143 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !291
  %144 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %143, i32 0, i32 4, !dbg !291
  %145 = load i8*, i8** %144, align 8, !dbg !291
  %146 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !291
  %147 = getelementptr inbounds %struct.ahci_host_priv, %struct.ahci_host_priv* %146, i32 0, i32 0, !dbg !291
  %148 = load i8*, i8** %147, align 8, !dbg !291
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([28 x i8], [28 x i8]* @.str.2, i32 0, i32 0), i8* %145, i8* %148), !dbg !291
  %149 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !292
  %150 = call i32 @xgene_ahci_mux_select(%struct.xgene_ahci_context* %149), !dbg !294
  store i32 %150, i32* %10, align 4, !dbg !295
  %151 = icmp ne i32 %150, 0, !dbg !295
  br i1 %151, label %ahci_xgene_h2.llbc-xgene_ahci_probe-30, label %ahci_xgene_h2.llbc-xgene_ahci_probe-31, !dbg !296

ahci_xgene_h2.llbc-xgene_ahci_probe-30:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-29
  %152 = load i32, i32* %10, align 4, !dbg !297
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([36 x i8], [36 x i8]* @.str.3, i32 0, i32 0), i32 %152), !dbg !297
  store i32 -19, i32* %1, align 4, !dbg !299
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !299

ahci_xgene_h2.llbc-xgene_ahci_probe-31:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-29
  %153 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !300
  %154 = call i32 @xgene_ahci_is_memram_inited(%struct.xgene_ahci_context* %153), !dbg !302
  %155 = icmp ne i32 %154, 0, !dbg !302
  br i1 %155, label %ahci_xgene_h2.llbc-xgene_ahci_probe-32, label %ahci_xgene_h2.llbc-xgene_ahci_probe-33, !dbg !303

ahci_xgene_h2.llbc-xgene_ahci_probe-32:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-31
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([35 x i8], [35 x i8]* @.str.4, i32 0, i32 0)), !dbg !304
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-38, !dbg !306

ahci_xgene_h2.llbc-xgene_ahci_probe-33:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-31
  %156 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !307
  %157 = call i32 @ahci_platform_enable_clks(%struct.ahci_host_priv* %156), !dbg !308
  store i32 %157, i32* %10, align 4, !dbg !309
  %158 = load i32, i32* %10, align 4, !dbg !310
  %159 = icmp ne i32 %158, 0, !dbg !310
  br i1 %159, label %ahci_xgene_h2.llbc-xgene_ahci_probe-34, label %ahci_xgene_h2.llbc-xgene_ahci_probe-35, !dbg !312

ahci_xgene_h2.llbc-xgene_ahci_probe-34:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-33
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-45, !dbg !313

ahci_xgene_h2.llbc-xgene_ahci_probe-35:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-33
  %160 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !314
  call void @ahci_platform_disable_clks(%struct.ahci_host_priv* %160), !dbg !315
  %161 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !316
  %162 = call i32 @ahci_platform_enable_resources(%struct.ahci_host_priv* %161), !dbg !317
  store i32 %162, i32* %10, align 4, !dbg !318
  %163 = load i32, i32* %10, align 4, !dbg !319
  %164 = icmp ne i32 %163, 0, !dbg !319
  br i1 %164, label %ahci_xgene_h2.llbc-xgene_ahci_probe-36, label %ahci_xgene_h2.llbc-xgene_ahci_probe-37, !dbg !321

ahci_xgene_h2.llbc-xgene_ahci_probe-36:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-35
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-45, !dbg !322

ahci_xgene_h2.llbc-xgene_ahci_probe-37:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-35
  %165 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !323
  call void @xgene_ahci_hw_init(%struct.ahci_host_priv* %165), !dbg !324
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-38, !dbg !324

ahci_xgene_h2.llbc-xgene_ahci_probe-38:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-37, %ahci_xgene_h2.llbc-xgene_ahci_probe-32
  %166 = load i32, i32* %8, align 4, !dbg !325
  switch i32 %166, label %ahci_xgene_h2.llbc-xgene_ahci_probe-41 [
    i32 1, label %ahci_xgene_h2.llbc-xgene_ahci_probe-39
    i32 2, label %ahci_xgene_h2.llbc-xgene_ahci_probe-40
  ], !dbg !326

ahci_xgene_h2.llbc-xgene_ahci_probe-39:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-38
  %167 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !327
  %168 = getelementptr inbounds %struct.ahci_host_priv, %struct.ahci_host_priv* %167, i32 0, i32 2, !dbg !329
  store i32 2, i32* %168, align 8, !dbg !330
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-42, !dbg !331

ahci_xgene_h2.llbc-xgene_ahci_probe-40:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-38
  %169 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !332
  %170 = getelementptr inbounds %struct.ahci_host_priv, %struct.ahci_host_priv* %169, i32 0, i32 2, !dbg !333
  %171 = load i32, i32* %170, align 8, !dbg !334
  %172 = or i32 %171, 4, !dbg !334
  store i32 %172, i32* %170, align 8, !dbg !334
  %173 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !335
  %174 = getelementptr inbounds %struct.ahci_host_priv, %struct.ahci_host_priv* %173, i32 0, i32 3, !dbg !336
  store i32 (i32, i8*)* @xgene_ahci_irq_intr, i32 (i32, i8*)** %174, align 8, !dbg !337
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-42, !dbg !338

ahci_xgene_h2.llbc-xgene_ahci_probe-41:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-38
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-42, !dbg !339

ahci_xgene_h2.llbc-xgene_ahci_probe-42:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-41, %ahci_xgene_h2.llbc-xgene_ahci_probe-40, %ahci_xgene_h2.llbc-xgene_ahci_probe-39
  %175 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !340
  %176 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !341
  %177 = load i32, i32* %8, align 4, !dbg !342
  %178 = sub i32 %177, 1, !dbg !343
  %179 = zext i32 %178 to i64, !dbg !344
  %180 = getelementptr inbounds [2 x %struct.device*], [2 x %struct.device*]* %9, i64 0, i64 %179, !dbg !344
  %181 = load %struct.device*, %struct.device** %180, align 8, !dbg !344
  %182 = call i32 @ahci_platform_init_host(%struct.platform_device* %175, %struct.ahci_host_priv* %176, %struct.device* %181, %struct.device* @ahci_platform_sht), !dbg !345
  store i32 %182, i32* %10, align 4, !dbg !346
  %183 = load i32, i32* %10, align 4, !dbg !347
  %184 = icmp ne i32 %183, 0, !dbg !347
  br i1 %184, label %ahci_xgene_h2.llbc-xgene_ahci_probe-43, label %ahci_xgene_h2.llbc-xgene_ahci_probe-44, !dbg !349

ahci_xgene_h2.llbc-xgene_ahci_probe-43:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-42
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-45, !dbg !350

ahci_xgene_h2.llbc-xgene_ahci_probe-44:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-42
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([41 x i8], [41 x i8]* @.str.5, i32 0, i32 0)), !dbg !351
  store i32 0, i32* %1, align 4, !dbg !352
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !352

ahci_xgene_h2.llbc-xgene_ahci_probe-45:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-43, %ahci_xgene_h2.llbc-xgene_ahci_probe-36, %ahci_xgene_h2.llbc-xgene_ahci_probe-34
  %185 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !353
  call void @ahci_platform_disable_resources(%struct.ahci_host_priv* %185), !dbg !354
  %186 = load i32, i32* %10, align 4, !dbg !355
  store i32 %186, i32* %1, align 4, !dbg !356
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !356

ahci_xgene_h2.llbc-xgene_ahci_probe-46:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-45, %ahci_xgene_h2.llbc-xgene_ahci_probe-44, %ahci_xgene_h2.llbc-xgene_ahci_probe-30, %ahci_xgene_h2.llbc-xgene_ahci_probe-12, %ahci_xgene_h2.llbc-xgene_ahci_probe-9, %ahci_xgene_h2.llbc-xgene_ahci_probe-7, %ahci_xgene_h2.llbc-xgene_ahci_probe-5, %ahci_xgene_h2.llbc-xgene_ahci_probe-3, %ahci_xgene_h2.llbc-xgene_ahci_probe-1
  %187 = load i32, i32* %1, align 4, !dbg !357
  ret i32 %187, !dbg !357
}

; Function Attrs: argmemonly nounwind
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* nocapture writeonly, i8* nocapture readonly, i64, i1) #2

; Function Attrs: noinline nounwind optnone uwtable
define internal %struct.ahci_host_priv* @ahci_platform_get_resources(%struct.platform_device*) #0 !dbg !358 {
ahci_xgene_h2.llbc-ahci_platform_get_resources-0:
  %1 = alloca %struct.platform_device*, align 8
  store %struct.platform_device* %0, %struct.platform_device** %1, align 8
  %2 = load %struct.platform_device*, %struct.platform_device** %1, align 8, !dbg !361
  ret %struct.ahci_host_priv* @global_hpriv, !dbg !362
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i8* @devm_kzalloc(%struct.device*, i64, i32) #0 !dbg !363 {
ahci_xgene_h2.llbc-devm_kzalloc-0:
  %3 = alloca %struct.device*, align 8
  %4 = alloca i64, align 8
  %5 = alloca i32, align 4
  store %struct.device* %0, %struct.device** %3, align 8
  store i64 %1, i64* %4, align 8
  store i32 %2, i32* %5, align 4
  %6 = load %struct.device*, %struct.device** %3, align 8, !dbg !368
  %7 = load i64, i64* %4, align 8, !dbg !369
  %8 = load i32, i32* %5, align 4, !dbg !370
  ret i8* bitcast (%struct.xgene_ahci_context* @global_ctx to i8*), !dbg !371
}

; Function Attrs: noinline nounwind optnone uwtable
define internal %struct.device* @platform_get_resource(%struct.platform_device*, i32, i32) #0 !dbg !372 {
ahci_xgene_h2.llbc-platform_get_resource-0:
  %3 = alloca %struct.device*, align 8
  %4 = alloca %struct.platform_device*, align 8
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  store %struct.platform_device* %0, %struct.platform_device** %4, align 8
  store i32 %1, i32* %5, align 4
  store i32 %2, i32* %6, align 4
  %7 = load %struct.platform_device*, %struct.platform_device** %4, align 8, !dbg !376
  %8 = load i32, i32* %5, align 4, !dbg !377
  %9 = load i32, i32* %6, align 4, !dbg !378
  %10 = icmp eq i32 %9, 4, !dbg !380
  br i1 %10, label %ahci_xgene_h2.llbc-platform_get_resource-1, label %ahci_xgene_h2.llbc-platform_get_resource-2, !dbg !381

ahci_xgene_h2.llbc-platform_get_resource-1:       ; preds = %ahci_xgene_h2.llbc-platform_get_resource-0
  store %struct.device* null, %struct.device** %3, align 8, !dbg !382
  br label %ahci_xgene_h2.llbc-platform_get_resource-3, !dbg !382

ahci_xgene_h2.llbc-platform_get_resource-2:       ; preds = %ahci_xgene_h2.llbc-platform_get_resource-0
  store %struct.device* @global_resource, %struct.device** %3, align 8, !dbg !383
  br label %ahci_xgene_h2.llbc-platform_get_resource-3, !dbg !383

ahci_xgene_h2.llbc-platform_get_resource-3:       ; preds = %ahci_xgene_h2.llbc-platform_get_resource-2, %ahci_xgene_h2.llbc-platform_get_resource-1
  %11 = load %struct.device*, %struct.device** %3, align 8, !dbg !384
  ret %struct.device* %11, !dbg !384
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i8* @devm_ioremap_resource(%struct.device*, %struct.device*) #0 !dbg !385 {
ahci_xgene_h2.llbc-devm_ioremap_resource-0:
  %2 = alloca %struct.device*, align 8
  %3 = alloca %struct.device*, align 8
  store %struct.device* %0, %struct.device** %2, align 8
  store %struct.device* %1, %struct.device** %3, align 8
  %4 = load %struct.device*, %struct.device** %2, align 8, !dbg !388
  %5 = load %struct.device*, %struct.device** %3, align 8, !dbg !389
  ret i8* inttoptr (i64 4096 to i8*), !dbg !390
}

; Function Attrs: noinline nounwind optnone uwtable
define internal %struct.of_device_id* @of_match_device(%struct.of_device_id*, %struct.device*) #0 !dbg !391 {
ahci_xgene_h2.llbc-of_match_device-0:
  %2 = alloca %struct.of_device_id*, align 8
  %3 = alloca %struct.device*, align 8
  store %struct.of_device_id* %0, %struct.of_device_id** %2, align 8
  store %struct.device* %1, %struct.device** %3, align 8
  %4 = load %struct.of_device_id*, %struct.of_device_id** %2, align 8, !dbg !397
  %5 = load %struct.device*, %struct.device** %3, align 8, !dbg !398
  ret %struct.of_device_id* null, !dbg !399
}

; Function Attrs: noinline nounwind optnone uwtable
define internal %struct.acpi_device_id* @acpi_match_device(%struct.acpi_device_id*, %struct.device*) #0 !dbg !400 {
ahci_xgene_h2.llbc-acpi_match_device-0:
  %2 = alloca %struct.acpi_device_id*, align 8
  %3 = alloca %struct.device*, align 8
  store %struct.acpi_device_id* %0, %struct.acpi_device_id** %2, align 8
  store %struct.device* %1, %struct.device** %3, align 8
  %4 = load %struct.acpi_device_id*, %struct.acpi_device_id** %2, align 8, !dbg !404
  %5 = load %struct.device*, %struct.device** %3, align 8, !dbg !405
  ret %struct.acpi_device_id* @global_acpi_id, !dbg !406
}

; Function Attrs: noinline nounwind optnone uwtable
define internal void @stub_log(i8*, ...) #0 !dbg !407 {
ahci_xgene_h2.llbc-stub_log-0:
  %1 = alloca i8*, align 8
  store i8* %0, i8** %1, align 8
  %2 = load i8*, i8** %1, align 8, !dbg !412
  ret void, !dbg !413
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @acpi_get_object_info(i64, %struct.acpi_device_info**) #0 !dbg !414 {
ahci_xgene_h2.llbc-acpi_get_object_info-0:
  %2 = alloca i64, align 8
  %3 = alloca %struct.acpi_device_info**, align 8
  store i64 %0, i64* %2, align 8
  store %struct.acpi_device_info** %1, %struct.acpi_device_info*** %3, align 8
  %4 = load i64, i64* %2, align 8, !dbg !425
  %5 = load %struct.acpi_device_info**, %struct.acpi_device_info*** %3, align 8, !dbg !426
  ret i32 1, !dbg !427
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @xgene_ahci_mux_select(%struct.xgene_ahci_context*) #0 !dbg !428 {
ahci_xgene_h2.llbc-xgene_ahci_mux_select-0:
  %1 = alloca %struct.xgene_ahci_context*, align 8
  store %struct.xgene_ahci_context* %0, %struct.xgene_ahci_context** %1, align 8
  %2 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %1, align 8, !dbg !432
  ret i32 0, !dbg !433
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @xgene_ahci_is_memram_inited(%struct.xgene_ahci_context*) #0 !dbg !434 {
ahci_xgene_h2.llbc-xgene_ahci_is_memram_inited-0:
  %1 = alloca %struct.xgene_ahci_context*, align 8
  store %struct.xgene_ahci_context* %0, %struct.xgene_ahci_context** %1, align 8
  %2 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %1, align 8, !dbg !435
  ret i32 1, !dbg !436
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @ahci_platform_enable_clks(%struct.ahci_host_priv*) #0 !dbg !437 {
ahci_xgene_h2.llbc-ahci_platform_enable_clks-0:
  %1 = alloca %struct.ahci_host_priv*, align 8
  store %struct.ahci_host_priv* %0, %struct.ahci_host_priv** %1, align 8
  %2 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %1, align 8, !dbg !440
  ret i32 0, !dbg !441
}

; Function Attrs: noinline nounwind optnone uwtable
define internal void @ahci_platform_disable_clks(%struct.ahci_host_priv*) #0 !dbg !442 {
ahci_xgene_h2.llbc-ahci_platform_disable_clks-0:
  %1 = alloca %struct.ahci_host_priv*, align 8
  store %struct.ahci_host_priv* %0, %struct.ahci_host_priv** %1, align 8
  %2 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %1, align 8, !dbg !445
  ret void, !dbg !446
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @ahci_platform_enable_resources(%struct.ahci_host_priv*) #0 !dbg !447 {
ahci_xgene_h2.llbc-ahci_platform_enable_resources-0:
  %1 = alloca %struct.ahci_host_priv*, align 8
  store %struct.ahci_host_priv* %0, %struct.ahci_host_priv** %1, align 8
  %2 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %1, align 8, !dbg !448
  ret i32 0, !dbg !449
}

; Function Attrs: noinline nounwind optnone uwtable
define internal void @xgene_ahci_hw_init(%struct.ahci_host_priv*) #0 !dbg !450 {
ahci_xgene_h2.llbc-xgene_ahci_hw_init-0:
  %1 = alloca %struct.ahci_host_priv*, align 8
  store %struct.ahci_host_priv* %0, %struct.ahci_host_priv** %1, align 8
  %2 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %1, align 8, !dbg !451
  ret void, !dbg !452
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @xgene_ahci_irq_intr(i32, i8*) #0 !dbg !453 {
ahci_xgene_h2.llbc-xgene_ahci_irq_intr-0:
  %2 = alloca i32, align 4
  %3 = alloca i8*, align 8
  store i32 %0, i32* %2, align 4
  store i8* %1, i8** %3, align 8
  %4 = load i32, i32* %2, align 4, !dbg !454
  %5 = load i8*, i8** %3, align 8, !dbg !455
  ret i32 0, !dbg !456
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @ahci_platform_init_host(%struct.platform_device*, %struct.ahci_host_priv*, %struct.device*, %struct.device*) #0 !dbg !457 {
ahci_xgene_h2.llbc-ahci_platform_init_host-0:
  %4 = alloca %struct.platform_device*, align 8
  %5 = alloca %struct.ahci_host_priv*, align 8
  %6 = alloca %struct.device*, align 8
  %7 = alloca %struct.device*, align 8
  store %struct.platform_device* %0, %struct.platform_device** %4, align 8
  store %struct.ahci_host_priv* %1, %struct.ahci_host_priv** %5, align 8
  store %struct.device* %2, %struct.device** %6, align 8
  store %struct.device* %3, %struct.device** %7, align 8
  %8 = load %struct.platform_device*, %struct.platform_device** %4, align 8, !dbg !462
  %9 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %5, align 8, !dbg !463
  %10 = load %struct.device*, %struct.device** %6, align 8, !dbg !464
  %11 = load %struct.device*, %struct.device** %7, align 8, !dbg !465
  ret i32 0, !dbg !466
}

; Function Attrs: noinline nounwind optnone uwtable
define internal void @ahci_platform_disable_resources(%struct.ahci_host_priv*) #0 !dbg !467 {
ahci_xgene_h2.llbc-ahci_platform_disable_resources-0:
  %1 = alloca %struct.ahci_host_priv*, align 8
  store %struct.ahci_host_priv* %0, %struct.ahci_host_priv** %1, align 8
  %2 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %1, align 8, !dbg !468
  ret void, !dbg !469
}

; Function Attrs: noinline nounwind uwtable
define dso_local i8* @memcpy(i8*, i8*, i64) #3 !dbg !470 {
  %4 = alloca i8*, align 8
  %5 = alloca i8*, align 8
  %6 = alloca i64, align 8
  %7 = alloca i8*, align 8
  %8 = alloca i8*, align 8
  store i8* %0, i8** %4, align 8
  store i8* %1, i8** %5, align 8
  store i64 %2, i64* %6, align 8
  %9 = load i8*, i8** %4, align 8, !dbg !475
  store i8* %9, i8** %7, align 8, !dbg !476
  %10 = load i8*, i8** %5, align 8, !dbg !477
  store i8* %10, i8** %8, align 8, !dbg !478
  br label %11, !dbg !479

; <label>:11:                                     ; preds = %15, %3
  %12 = load i64, i64* %6, align 8, !dbg !480
  %13 = add i64 %12, -1, !dbg !480
  store i64 %13, i64* %6, align 8, !dbg !480
  %14 = icmp ugt i64 %12, 0, !dbg !481
  br i1 %14, label %15, label %21, !dbg !479

; <label>:15:                                     ; preds = %11
  %16 = load i8*, i8** %8, align 8, !dbg !482
  %17 = getelementptr inbounds i8, i8* %16, i32 1, !dbg !482
  store i8* %17, i8** %8, align 8, !dbg !482
  %18 = load i8, i8* %16, align 1, !dbg !483
  %19 = load i8*, i8** %7, align 8, !dbg !484
  %20 = getelementptr inbounds i8, i8* %19, i32 1, !dbg !484
  store i8* %20, i8** %7, align 8, !dbg !484
  store i8 %18, i8* %19, align 1, !dbg !485
  br label %11, !dbg !479, !llvm.loop !486

; <label>:21:                                     ; preds = %11
  %22 = load i8*, i8** %4, align 8, !dbg !487
  ret i8* %22, !dbg !488
}

attributes #0 = { noinline nounwind optnone uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { nounwind readnone speculatable }
attributes #2 = { argmemonly nounwind }
attributes #3 = { noinline nounwind uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }

!llvm.dbg.cu = !{!2, !108}
!llvm.ident = !{!111, !111}
!llvm.module.flags = !{!112, !113, !114}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "stub_acpi_handle", scope: !2, file: !3, line: 90, type: !107, isLocal: true, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C99, file: !3, producer: "clang version 7.0.0 (tags/RELEASE_700/final)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !4, retainedTypes: !10, globals: !16)
!3 = !DIFile(filename: "ahci_xgene_h2.c", directory: "/work/history/ahci_xgene/runs/HIST-20261027T1322Z/h2")
!4 = !{!5}
!5 = !DICompositeType(tag: DW_TAG_enumeration_type, name: "xgene_ahci_version", file: !3, line: 68, baseType: !6, size: 32, elements: !7)
!6 = !DIBasicType(name: "unsigned int", size: 32, encoding: DW_ATE_unsigned)
!7 = !{!8, !9}
!8 = !DIEnumerator(name: "XGENE_AHCI_V1", value: 1, isUnsigned: true)
!9 = !DIEnumerator(name: "XGENE_AHCI_V2", value: 2, isUnsigned: true)
!10 = !{!11, !12, !14, !5, !15}
!11 = !DIBasicType(name: "long unsigned int", size: 64, encoding: DW_ATE_unsigned)
!12 = !DIDerivedType(tag: DW_TAG_typedef, name: "uintptr_t", file: !13, line: 79, baseType: !11)
!13 = !DIFile(filename: "/usr/include/stdint.h", directory: "/work/history/ahci_xgene/runs/HIST-20261027T1322Z/h2")
!14 = !DIBasicType(name: "long int", size: 64, encoding: DW_ATE_signed)
!15 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!16 = !{!17, !0, !26, !32, !34, !46, !70, !75, !86, !96, !102}
!17 = !DIGlobalVariableExpression(var: !18, expr: !DIExpression())
!18 = distinct !DIGlobalVariable(name: "global_pdev", scope: !2, file: !3, line: 84, type: !19, isLocal: true, isDefinition: true)
!19 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "platform_device", file: !3, line: 39, size: 32, elements: !20)
!20 = !{!21}
!21 = !DIDerivedType(tag: DW_TAG_member, name: "dev", scope: !19, file: !3, line: 39, baseType: !22, size: 32)
!22 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "device", file: !3, line: 38, size: 32, elements: !23)
!23 = !{!24}
!24 = !DIDerivedType(tag: DW_TAG_member, name: "unused", scope: !22, file: !3, line: 38, baseType: !25, size: 32)
!25 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!26 = !DIGlobalVariableExpression(var: !27, expr: !DIExpression())
!27 = distinct !DIGlobalVariable(name: "xgene_ahci_v1_port_info", scope: !2, file: !3, line: 73, type: !28, isLocal: true, isDefinition: true)
!28 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !29)
!29 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "ata_port_info", file: !3, line: 53, size: 32, elements: !30)
!30 = !{!31}
!31 = !DIDerivedType(tag: DW_TAG_member, name: "unused", scope: !29, file: !3, line: 53, baseType: !25, size: 32)
!32 = !DIGlobalVariableExpression(var: !33, expr: !DIExpression())
!33 = distinct !DIGlobalVariable(name: "xgene_ahci_v2_port_info", scope: !2, file: !3, line: 74, type: !28, isLocal: true, isDefinition: true)
!34 = !DIGlobalVariableExpression(var: !35, expr: !DIExpression())
!35 = distinct !DIGlobalVariable(name: "global_hpriv", scope: !2, file: !3, line: 85, type: !36, isLocal: true, isDefinition: true)
!36 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "ahci_host_priv", file: !3, line: 47, size: 256, elements: !37)
!37 = !{!38, !39, !40, !41}
!38 = !DIDerivedType(tag: DW_TAG_member, name: "mmio", scope: !36, file: !3, line: 48, baseType: !15, size: 64)
!39 = !DIDerivedType(tag: DW_TAG_member, name: "plat_data", scope: !36, file: !3, line: 49, baseType: !15, size: 64, offset: 64)
!40 = !DIDerivedType(tag: DW_TAG_member, name: "flags", scope: !36, file: !3, line: 50, baseType: !6, size: 32, offset: 128)
!41 = !DIDerivedType(tag: DW_TAG_member, name: "irq_handler", scope: !36, file: !3, line: 51, baseType: !42, size: 64, offset: 192)
!42 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !43, size: 64)
!43 = !DISubroutineType(types: !44)
!44 = !{!45, !25, !15}
!45 = !DIDerivedType(tag: DW_TAG_typedef, name: "irqreturn_t", file: !3, line: 20, baseType: !25)
!46 = !DIGlobalVariableExpression(var: !47, expr: !DIExpression())
!47 = distinct !DIGlobalVariable(name: "global_ctx", scope: !2, file: !3, line: 86, type: !48, isLocal: true, isDefinition: true)
!48 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "xgene_ahci_context", file: !3, line: 57, size: 512, elements: !49)
!49 = !{!50, !52, !54, !59, !66, !67, !68, !69}
!50 = !DIDerivedType(tag: DW_TAG_member, name: "hpriv", scope: !48, file: !3, line: 58, baseType: !51, size: 64)
!51 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !36, size: 64)
!52 = !DIDerivedType(tag: DW_TAG_member, name: "dev", scope: !48, file: !3, line: 59, baseType: !53, size: 64, offset: 64)
!53 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !22, size: 64)
!54 = !DIDerivedType(tag: DW_TAG_member, name: "last_cmd", scope: !48, file: !3, line: 60, baseType: !55, size: 16, offset: 128)
!55 = !DICompositeType(tag: DW_TAG_array_type, baseType: !56, size: 16, elements: !57)
!56 = !DIBasicType(name: "unsigned char", size: 8, encoding: DW_ATE_unsigned_char)
!57 = !{!58}
!58 = !DISubrange(count: 2)
!59 = !DIDerivedType(tag: DW_TAG_member, name: "class", scope: !48, file: !3, line: 61, baseType: !60, size: 64, offset: 160)
!60 = !DICompositeType(tag: DW_TAG_array_type, baseType: !61, size: 64, elements: !57)
!61 = !DIDerivedType(tag: DW_TAG_typedef, name: "u32", file: !3, line: 17, baseType: !62)
!62 = !DIDerivedType(tag: DW_TAG_typedef, name: "uint32_t", file: !63, line: 26, baseType: !64)
!63 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/stdint-uintn.h", directory: "/work/history/ahci_xgene/runs/HIST-20261027T1322Z/h2")
!64 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint32_t", file: !65, line: 42, baseType: !6)
!65 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types.h", directory: "/work/history/ahci_xgene/runs/HIST-20261027T1322Z/h2")
!66 = !DIDerivedType(tag: DW_TAG_member, name: "csr_core", scope: !48, file: !3, line: 62, baseType: !15, size: 64, offset: 256)
!67 = !DIDerivedType(tag: DW_TAG_member, name: "csr_diag", scope: !48, file: !3, line: 63, baseType: !15, size: 64, offset: 320)
!68 = !DIDerivedType(tag: DW_TAG_member, name: "csr_axi", scope: !48, file: !3, line: 64, baseType: !15, size: 64, offset: 384)
!69 = !DIDerivedType(tag: DW_TAG_member, name: "csr_mux", scope: !48, file: !3, line: 65, baseType: !15, size: 64, offset: 448)
!70 = !DIGlobalVariableExpression(var: !71, expr: !DIExpression())
!71 = distinct !DIGlobalVariable(name: "global_resource", scope: !2, file: !3, line: 87, type: !72, isLocal: true, isDefinition: true)
!72 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "resource", file: !3, line: 40, size: 32, elements: !73)
!73 = !{!74}
!74 = !DIDerivedType(tag: DW_TAG_member, name: "unused", scope: !72, file: !3, line: 40, baseType: !25, size: 32)
!75 = !DIGlobalVariableExpression(var: !76, expr: !DIExpression())
!76 = distinct !DIGlobalVariable(name: "xgene_ahci_of_match", scope: !2, file: !3, line: 81, type: !77, isLocal: true, isDefinition: true)
!77 = !DICompositeType(tag: DW_TAG_array_type, baseType: !78, size: 64, elements: !84)
!78 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !79)
!79 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "of_device_id", file: !3, line: 41, size: 64, elements: !80)
!80 = !{!81}
!81 = !DIDerivedType(tag: DW_TAG_member, name: "data", scope: !79, file: !3, line: 41, baseType: !82, size: 64)
!82 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !83, size: 64)
!83 = !DIDerivedType(tag: DW_TAG_const_type, baseType: null)
!84 = !{!85}
!85 = !DISubrange(count: 1)
!86 = !DIGlobalVariableExpression(var: !87, expr: !DIExpression())
!87 = distinct !DIGlobalVariable(name: "global_acpi_id", scope: !2, file: !3, line: 89, type: !88, isLocal: true, isDefinition: true)
!88 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "acpi_device_id", file: !3, line: 42, size: 192, elements: !89)
!89 = !{!90, !95}
!90 = !DIDerivedType(tag: DW_TAG_member, name: "id", scope: !88, file: !3, line: 42, baseType: !91, size: 128)
!91 = !DICompositeType(tag: DW_TAG_array_type, baseType: !92, size: 128, elements: !93)
!92 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!93 = !{!94}
!94 = !DISubrange(count: 16)
!95 = !DIDerivedType(tag: DW_TAG_member, name: "driver_data", scope: !88, file: !3, line: 42, baseType: !11, size: 64, offset: 128)
!96 = !DIGlobalVariableExpression(var: !97, expr: !DIExpression())
!97 = distinct !DIGlobalVariable(name: "xgene_ahci_acpi_match", scope: !2, file: !3, line: 76, type: !98, isLocal: true, isDefinition: true)
!98 = !DICompositeType(tag: DW_TAG_array_type, baseType: !99, size: 576, elements: !100)
!99 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !88)
!100 = !{!101}
!101 = !DISubrange(count: 3)
!102 = !DIGlobalVariableExpression(var: !103, expr: !DIExpression())
!103 = distinct !DIGlobalVariable(name: "ahci_platform_sht", scope: !2, file: !3, line: 75, type: !104, isLocal: true, isDefinition: true)
!104 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "scsi_host_template", file: !3, line: 54, size: 32, elements: !105)
!105 = !{!106}
!106 = !DIDerivedType(tag: DW_TAG_member, name: "unused", scope: !104, file: !3, line: 54, baseType: !25, size: 32)
!107 = !DIDerivedType(tag: DW_TAG_volatile_type, baseType: !11)
!108 = distinct !DICompileUnit(language: DW_LANG_C89, file: !109, producer: "clang version 7.0.0 (tags/RELEASE_700/final)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !110)
!109 = !DIFile(filename: "/work/source/UBITect/KLEE/klee/runtime/FreeStanding/memcpy.c", directory: "/work/build/klee-original/runtime/FreeStanding")
!110 = !{}
!111 = !{!"clang version 7.0.0 (tags/RELEASE_700/final)"}
!112 = !{i32 2, !"Dwarf Version", i32 4}
!113 = !{i32 2, !"Debug Info Version", i32 3}
!114 = !{i32 1, !"wchar_size", i32 4}
!115 = distinct !DISubprogram(name: "history_entry", scope: !116, file: !116, line: 2, type: !117, isLocal: true, isDefinition: true, scopeLine: 3, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!116 = !DIFile(filename: "history_entry.c", directory: "/work/history/ahci_xgene/runs/HIST-20261027T1322Z/h2")
!117 = !DISubroutineType(types: !118)
!118 = !{!25, !25}
!119 = !DILocation(line: 4, column: 39, scope: !115)
!120 = !DILocation(line: 4, column: 24, scope: !115)
!121 = !DILocation(line: 4, column: 22, scope: !115)
!122 = !DILocation(line: 5, column: 12, scope: !115)
!123 = !DILocation(line: 5, column: 5, scope: !115)
!124 = distinct !DISubprogram(name: "history_entry_failure", scope: !116, file: !116, line: 15, type: !117, isLocal: true, isDefinition: true, scopeLine: 16, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!125 = !DILocation(line: 17, column: 9, scope: !126)
!126 = distinct !DILexicalBlock(scope: !124, file: !116, line: 17, column: 9)
!127 = !DILocation(line: 17, column: 27, scope: !126)
!128 = !DILocation(line: 17, column: 9, scope: !124)
!129 = !DILocation(line: 18, column: 9, scope: !126)
!130 = !DILocation(line: 19, column: 22, scope: !124)
!131 = !DILocation(line: 20, column: 12, scope: !124)
!132 = !DILocation(line: 20, column: 5, scope: !124)
!133 = !DILocation(line: 21, column: 1, scope: !124)
!134 = distinct !DISubprogram(name: "xgene_ahci_probe", scope: !135, file: !135, line: 750, type: !136, isLocal: true, isDefinition: true, scopeLine: 751, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!135 = !DIFile(filename: "drivers/ata/ahci_xgene.c", directory: "/work/history/ahci_xgene/runs/HIST-20261027T1322Z/h2")
!136 = !DISubroutineType(types: !137)
!137 = !{!25, !138}
!138 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !19, size: 64)
!139 = !DILocation(line: 752, column: 24, scope: !134)
!140 = !DILocation(line: 752, column: 30, scope: !134)
!141 = !DILocation(line: 752, column: 17, scope: !134)
!142 = !DILocation(line: 757, column: 26, scope: !134)
!143 = !DILocation(line: 758, column: 30, scope: !134)
!144 = !DILocation(line: 762, column: 38, scope: !134)
!145 = !DILocation(line: 762, column: 10, scope: !134)
!146 = !DILocation(line: 762, column: 8, scope: !134)
!147 = !DILocation(line: 763, column: 6, scope: !148)
!148 = distinct !DILexicalBlock(scope: !134, file: !135, line: 763, column: 6)
!149 = !DILocation(line: 763, column: 6, scope: !134)
!150 = !DILocation(line: 764, column: 10, scope: !148)
!151 = !DILocation(line: 764, column: 3, scope: !148)
!152 = !DILocation(line: 766, column: 21, scope: !134)
!153 = !DILocation(line: 766, column: 8, scope: !134)
!154 = !DILocation(line: 766, column: 6, scope: !134)
!155 = !DILocation(line: 767, column: 7, scope: !156)
!156 = distinct !DILexicalBlock(scope: !134, file: !135, line: 767, column: 6)
!157 = !DILocation(line: 767, column: 6, scope: !134)
!158 = !DILocation(line: 768, column: 3, scope: !156)
!159 = !DILocation(line: 770, column: 21, scope: !134)
!160 = !DILocation(line: 770, column: 2, scope: !134)
!161 = !DILocation(line: 770, column: 9, scope: !134)
!162 = !DILocation(line: 770, column: 19, scope: !134)
!163 = !DILocation(line: 771, column: 15, scope: !134)
!164 = !DILocation(line: 771, column: 2, scope: !134)
!165 = !DILocation(line: 771, column: 7, scope: !134)
!166 = !DILocation(line: 771, column: 13, scope: !134)
!167 = !DILocation(line: 772, column: 13, scope: !134)
!168 = !DILocation(line: 772, column: 2, scope: !134)
!169 = !DILocation(line: 772, column: 7, scope: !134)
!170 = !DILocation(line: 772, column: 11, scope: !134)
!171 = !DILocation(line: 775, column: 30, scope: !134)
!172 = !DILocation(line: 775, column: 8, scope: !134)
!173 = !DILocation(line: 775, column: 6, scope: !134)
!174 = !DILocation(line: 776, column: 40, scope: !134)
!175 = !DILocation(line: 776, column: 45, scope: !134)
!176 = !DILocation(line: 776, column: 18, scope: !134)
!177 = !DILocation(line: 776, column: 2, scope: !134)
!178 = !DILocation(line: 776, column: 7, scope: !134)
!179 = !DILocation(line: 776, column: 16, scope: !134)
!180 = !DILocation(line: 777, column: 6, scope: !181)
!181 = distinct !DILexicalBlock(scope: !134, file: !135, line: 777, column: 6)
!182 = !DILocation(line: 777, column: 6, scope: !134)
!183 = !DILocation(line: 778, column: 10, scope: !181)
!184 = !DILocation(line: 778, column: 3, scope: !181)
!185 = !DILocation(line: 781, column: 30, scope: !134)
!186 = !DILocation(line: 781, column: 8, scope: !134)
!187 = !DILocation(line: 781, column: 6, scope: !134)
!188 = !DILocation(line: 782, column: 40, scope: !134)
!189 = !DILocation(line: 782, column: 45, scope: !134)
!190 = !DILocation(line: 782, column: 18, scope: !134)
!191 = !DILocation(line: 782, column: 2, scope: !134)
!192 = !DILocation(line: 782, column: 7, scope: !134)
!193 = !DILocation(line: 782, column: 16, scope: !134)
!194 = !DILocation(line: 783, column: 6, scope: !195)
!195 = distinct !DILexicalBlock(scope: !134, file: !135, line: 783, column: 6)
!196 = !DILocation(line: 783, column: 6, scope: !134)
!197 = !DILocation(line: 784, column: 10, scope: !195)
!198 = !DILocation(line: 784, column: 3, scope: !195)
!199 = !DILocation(line: 787, column: 30, scope: !134)
!200 = !DILocation(line: 787, column: 8, scope: !134)
!201 = !DILocation(line: 787, column: 6, scope: !134)
!202 = !DILocation(line: 788, column: 39, scope: !134)
!203 = !DILocation(line: 788, column: 44, scope: !134)
!204 = !DILocation(line: 788, column: 17, scope: !134)
!205 = !DILocation(line: 788, column: 2, scope: !134)
!206 = !DILocation(line: 788, column: 7, scope: !134)
!207 = !DILocation(line: 788, column: 15, scope: !134)
!208 = !DILocation(line: 789, column: 6, scope: !209)
!209 = distinct !DILexicalBlock(scope: !134, file: !135, line: 789, column: 6)
!210 = !DILocation(line: 789, column: 6, scope: !134)
!211 = !DILocation(line: 790, column: 10, scope: !209)
!212 = !DILocation(line: 790, column: 3, scope: !209)
!213 = !DILocation(line: 793, column: 30, scope: !134)
!214 = !DILocation(line: 793, column: 8, scope: !134)
!215 = !DILocation(line: 793, column: 6, scope: !134)
!216 = !DILocation(line: 794, column: 6, scope: !217)
!217 = distinct !DILexicalBlock(scope: !134, file: !135, line: 794, column: 6)
!218 = !DILocation(line: 794, column: 6, scope: !134)
!219 = !DILocation(line: 795, column: 45, scope: !220)
!220 = distinct !DILexicalBlock(scope: !217, file: !135, line: 794, column: 11)
!221 = !DILocation(line: 795, column: 50, scope: !220)
!222 = !DILocation(line: 795, column: 23, scope: !220)
!223 = !DILocation(line: 795, column: 17, scope: !220)
!224 = !DILocation(line: 796, column: 7, scope: !225)
!225 = distinct !DILexicalBlock(scope: !220, file: !135, line: 796, column: 7)
!226 = !DILocation(line: 796, column: 7, scope: !220)
!227 = !DILocation(line: 797, column: 11, scope: !225)
!228 = !DILocation(line: 797, column: 4, scope: !225)
!229 = !DILocation(line: 799, column: 18, scope: !220)
!230 = !DILocation(line: 799, column: 3, scope: !220)
!231 = !DILocation(line: 799, column: 8, scope: !220)
!232 = !DILocation(line: 799, column: 16, scope: !220)
!233 = !DILocation(line: 800, column: 2, scope: !220)
!234 = !DILocation(line: 802, column: 50, scope: !134)
!235 = !DILocation(line: 802, column: 13, scope: !134)
!236 = !DILocation(line: 802, column: 11, scope: !134)
!237 = !DILocation(line: 803, column: 6, scope: !238)
!238 = distinct !DILexicalBlock(scope: !134, file: !135, line: 803, column: 6)
!239 = !DILocation(line: 803, column: 6, scope: !134)
!240 = !DILocation(line: 804, column: 7, scope: !241)
!241 = distinct !DILexicalBlock(scope: !242, file: !135, line: 804, column: 7)
!242 = distinct !DILexicalBlock(scope: !238, file: !135, line: 803, column: 16)
!243 = !DILocation(line: 804, column: 17, scope: !241)
!244 = !DILocation(line: 804, column: 7, scope: !242)
!245 = !DILocation(line: 805, column: 40, scope: !241)
!246 = !DILocation(line: 805, column: 50, scope: !241)
!247 = !DILocation(line: 805, column: 14, scope: !241)
!248 = !DILocation(line: 805, column: 12, scope: !241)
!249 = !DILocation(line: 805, column: 4, scope: !241)
!250 = !DILocation(line: 806, column: 2, scope: !242)
!251 = !DILocation(line: 813, column: 55, scope: !252)
!252 = distinct !DILexicalBlock(scope: !238, file: !135, line: 808, column: 7)
!253 = !DILocation(line: 813, column: 61, scope: !252)
!254 = !DILocation(line: 813, column: 13, scope: !252)
!255 = !DILocation(line: 813, column: 11, scope: !252)
!256 = !DILocation(line: 814, column: 8, scope: !257)
!257 = distinct !DILexicalBlock(scope: !252, file: !135, line: 814, column: 7)
!258 = !DILocation(line: 814, column: 7, scope: !252)
!259 = !DILocation(line: 815, column: 4, scope: !260)
!260 = distinct !DILexicalBlock(scope: !257, file: !135, line: 814, column: 17)
!261 = !DILocation(line: 816, column: 12, scope: !260)
!262 = !DILocation(line: 817, column: 3, scope: !260)
!263 = !DILocation(line: 817, column: 14, scope: !264)
!264 = distinct !DILexicalBlock(scope: !257, file: !135, line: 817, column: 14)
!265 = !DILocation(line: 817, column: 23, scope: !264)
!266 = !DILocation(line: 817, column: 14, scope: !257)
!267 = !DILocation(line: 818, column: 40, scope: !268)
!268 = distinct !DILexicalBlock(scope: !264, file: !135, line: 817, column: 36)
!269 = !DILocation(line: 818, column: 49, scope: !268)
!270 = !DILocation(line: 818, column: 14, scope: !268)
!271 = !DILocation(line: 818, column: 12, scope: !268)
!272 = !DILocation(line: 819, column: 34, scope: !268)
!273 = !DILocation(line: 819, column: 13, scope: !268)
!274 = !DILocation(line: 819, column: 11, scope: !268)
!275 = !DILocation(line: 820, column: 8, scope: !276)
!276 = distinct !DILexicalBlock(scope: !268, file: !135, line: 820, column: 8)
!277 = !DILocation(line: 820, column: 8, scope: !268)
!278 = !DILocation(line: 821, column: 5, scope: !279)
!279 = distinct !DILexicalBlock(scope: !276, file: !135, line: 820, column: 30)
!280 = !DILocation(line: 823, column: 13, scope: !279)
!281 = !DILocation(line: 824, column: 4, scope: !279)
!282 = !DILocation(line: 824, column: 15, scope: !283)
!283 = distinct !DILexicalBlock(scope: !276, file: !135, line: 824, column: 15)
!284 = !DILocation(line: 824, column: 21, scope: !283)
!285 = !DILocation(line: 824, column: 27, scope: !283)
!286 = !DILocation(line: 824, column: 15, scope: !276)
!287 = !DILocation(line: 825, column: 13, scope: !288)
!288 = distinct !DILexicalBlock(scope: !283, file: !135, line: 824, column: 45)
!289 = !DILocation(line: 826, column: 4, scope: !288)
!290 = !DILocation(line: 827, column: 3, scope: !268)
!291 = !DILocation(line: 831, column: 2, scope: !134)
!292 = !DILocation(line: 835, column: 34, scope: !293)
!293 = distinct !DILexicalBlock(scope: !134, file: !135, line: 835, column: 6)
!294 = !DILocation(line: 835, column: 12, scope: !293)
!295 = !DILocation(line: 835, column: 10, scope: !293)
!296 = !DILocation(line: 835, column: 6, scope: !134)
!297 = !DILocation(line: 836, column: 3, scope: !298)
!298 = distinct !DILexicalBlock(scope: !293, file: !135, line: 835, column: 41)
!299 = !DILocation(line: 837, column: 3, scope: !298)
!300 = !DILocation(line: 840, column: 34, scope: !301)
!301 = distinct !DILexicalBlock(scope: !134, file: !135, line: 840, column: 6)
!302 = !DILocation(line: 840, column: 6, scope: !301)
!303 = !DILocation(line: 840, column: 6, scope: !134)
!304 = !DILocation(line: 841, column: 3, scope: !305)
!305 = distinct !DILexicalBlock(scope: !301, file: !135, line: 840, column: 40)
!306 = !DILocation(line: 842, column: 3, scope: !305)
!307 = !DILocation(line: 846, column: 33, scope: !134)
!308 = !DILocation(line: 846, column: 7, scope: !134)
!309 = !DILocation(line: 846, column: 5, scope: !134)
!310 = !DILocation(line: 847, column: 6, scope: !311)
!311 = distinct !DILexicalBlock(scope: !134, file: !135, line: 847, column: 6)
!312 = !DILocation(line: 847, column: 6, scope: !134)
!313 = !DILocation(line: 848, column: 3, scope: !311)
!314 = !DILocation(line: 849, column: 29, scope: !134)
!315 = !DILocation(line: 849, column: 2, scope: !134)
!316 = !DILocation(line: 851, column: 38, scope: !134)
!317 = !DILocation(line: 851, column: 7, scope: !134)
!318 = !DILocation(line: 851, column: 5, scope: !134)
!319 = !DILocation(line: 852, column: 6, scope: !320)
!320 = distinct !DILexicalBlock(scope: !134, file: !135, line: 852, column: 6)
!321 = !DILocation(line: 852, column: 6, scope: !134)
!322 = !DILocation(line: 853, column: 3, scope: !320)
!323 = !DILocation(line: 856, column: 21, scope: !134)
!324 = !DILocation(line: 856, column: 2, scope: !134)
!325 = !DILocation(line: 859, column: 10, scope: !134)
!326 = !DILocation(line: 859, column: 2, scope: !134)
!327 = !DILocation(line: 861, column: 3, scope: !328)
!328 = distinct !DILexicalBlock(scope: !134, file: !135, line: 859, column: 19)
!329 = !DILocation(line: 861, column: 10, scope: !328)
!330 = !DILocation(line: 861, column: 16, scope: !328)
!331 = !DILocation(line: 862, column: 3, scope: !328)
!332 = !DILocation(line: 864, column: 3, scope: !328)
!333 = !DILocation(line: 864, column: 10, scope: !328)
!334 = !DILocation(line: 864, column: 16, scope: !328)
!335 = !DILocation(line: 865, column: 3, scope: !328)
!336 = !DILocation(line: 865, column: 10, scope: !328)
!337 = !DILocation(line: 865, column: 22, scope: !328)
!338 = !DILocation(line: 866, column: 3, scope: !328)
!339 = !DILocation(line: 868, column: 3, scope: !328)
!340 = !DILocation(line: 871, column: 31, scope: !134)
!341 = !DILocation(line: 871, column: 37, scope: !134)
!342 = !DILocation(line: 871, column: 48, scope: !134)
!343 = !DILocation(line: 871, column: 56, scope: !134)
!344 = !DILocation(line: 871, column: 44, scope: !134)
!345 = !DILocation(line: 871, column: 7, scope: !134)
!346 = !DILocation(line: 871, column: 5, scope: !134)
!347 = !DILocation(line: 873, column: 6, scope: !348)
!348 = distinct !DILexicalBlock(scope: !134, file: !135, line: 873, column: 6)
!349 = !DILocation(line: 873, column: 6, scope: !134)
!350 = !DILocation(line: 874, column: 3, scope: !348)
!351 = !DILocation(line: 876, column: 2, scope: !134)
!352 = !DILocation(line: 877, column: 2, scope: !134)
!353 = !DILocation(line: 880, column: 34, scope: !134)
!354 = !DILocation(line: 880, column: 2, scope: !134)
!355 = !DILocation(line: 881, column: 9, scope: !134)
!356 = !DILocation(line: 881, column: 2, scope: !134)
!357 = !DILocation(line: 882, column: 1, scope: !134)
!358 = distinct !DISubprogram(name: "ahci_platform_get_resources", scope: !3, file: !3, line: 109, type: !359, isLocal: true, isDefinition: true, scopeLine: 110, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!359 = !DISubroutineType(types: !360)
!360 = !{!51, !138}
!361 = !DILocation(line: 111, column: 11, scope: !358)
!362 = !DILocation(line: 112, column: 5, scope: !358)
!363 = distinct !DISubprogram(name: "devm_kzalloc", scope: !3, file: !3, line: 115, type: !364, isLocal: true, isDefinition: true, scopeLine: 116, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!364 = !DISubroutineType(types: !365)
!365 = !{!15, !53, !366, !6}
!366 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !367, line: 62, baseType: !11)
!367 = !DIFile(filename: "/opt/llvm7/lib/clang/7.0.0/include/stddef.h", directory: "/work/history/ahci_xgene/runs/HIST-20261027T1322Z/h2")
!368 = !DILocation(line: 117, column: 11, scope: !363)
!369 = !DILocation(line: 118, column: 11, scope: !363)
!370 = !DILocation(line: 119, column: 11, scope: !363)
!371 = !DILocation(line: 120, column: 5, scope: !363)
!372 = distinct !DISubprogram(name: "platform_get_resource", scope: !3, file: !3, line: 123, type: !373, isLocal: true, isDefinition: true, scopeLine: 126, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!373 = !DISubroutineType(types: !374)
!374 = !{!375, !138, !6, !6}
!375 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !72, size: 64)
!376 = !DILocation(line: 127, column: 11, scope: !372)
!377 = !DILocation(line: 128, column: 11, scope: !372)
!378 = !DILocation(line: 129, column: 9, scope: !379)
!379 = distinct !DILexicalBlock(scope: !372, file: !3, line: 129, column: 9)
!380 = !DILocation(line: 129, column: 13, scope: !379)
!381 = !DILocation(line: 129, column: 9, scope: !372)
!382 = !DILocation(line: 130, column: 9, scope: !379)
!383 = !DILocation(line: 131, column: 5, scope: !372)
!384 = !DILocation(line: 132, column: 1, scope: !372)
!385 = distinct !DISubprogram(name: "devm_ioremap_resource", scope: !3, file: !3, line: 134, type: !386, isLocal: true, isDefinition: true, scopeLine: 135, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!386 = !DISubroutineType(types: !387)
!387 = !{!15, !53, !375}
!388 = !DILocation(line: 136, column: 11, scope: !385)
!389 = !DILocation(line: 137, column: 11, scope: !385)
!390 = !DILocation(line: 138, column: 5, scope: !385)
!391 = distinct !DISubprogram(name: "of_match_device", scope: !3, file: !3, line: 141, type: !392, isLocal: true, isDefinition: true, scopeLine: 143, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!392 = !DISubroutineType(types: !393)
!393 = !{!394, !394, !395}
!394 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !78, size: 64)
!395 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !396, size: 64)
!396 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !22)
!397 = !DILocation(line: 144, column: 11, scope: !391)
!398 = !DILocation(line: 145, column: 11, scope: !391)
!399 = !DILocation(line: 146, column: 5, scope: !391)
!400 = distinct !DISubprogram(name: "acpi_match_device", scope: !3, file: !3, line: 149, type: !401, isLocal: true, isDefinition: true, scopeLine: 151, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!401 = !DISubroutineType(types: !402)
!402 = !{!403, !403, !395}
!403 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !99, size: 64)
!404 = !DILocation(line: 152, column: 11, scope: !400)
!405 = !DILocation(line: 153, column: 11, scope: !400)
!406 = !DILocation(line: 154, column: 5, scope: !400)
!407 = distinct !DISubprogram(name: "stub_log", scope: !3, file: !3, line: 99, type: !408, isLocal: true, isDefinition: true, scopeLine: 100, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!408 = !DISubroutineType(types: !409)
!409 = !{null, !410, null}
!410 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !411, size: 64)
!411 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !92)
!412 = !DILocation(line: 101, column: 11, scope: !407)
!413 = !DILocation(line: 102, column: 1, scope: !407)
!414 = distinct !DISubprogram(name: "acpi_get_object_info", scope: !3, file: !3, line: 165, type: !415, isLocal: true, isDefinition: true, scopeLine: 167, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!415 = !DISubroutineType(types: !416)
!416 = !{!417, !418, !419}
!417 = !DIDerivedType(tag: DW_TAG_typedef, name: "acpi_status", file: !3, line: 19, baseType: !25)
!418 = !DIDerivedType(tag: DW_TAG_typedef, name: "acpi_handle", file: !3, line: 18, baseType: !11)
!419 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !420, size: 64)
!420 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !421, size: 64)
!421 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "acpi_device_info", file: !3, line: 46, size: 64, elements: !422)
!422 = !{!423, !424}
!423 = !DIDerivedType(tag: DW_TAG_member, name: "valid", scope: !421, file: !3, line: 46, baseType: !6, size: 32)
!424 = !DIDerivedType(tag: DW_TAG_member, name: "reserved", scope: !421, file: !3, line: 46, baseType: !6, size: 32, offset: 32)
!425 = !DILocation(line: 174, column: 11, scope: !414)
!426 = !DILocation(line: 175, column: 11, scope: !414)
!427 = !DILocation(line: 176, column: 5, scope: !414)
!428 = distinct !DISubprogram(name: "xgene_ahci_mux_select", scope: !3, file: !3, line: 187, type: !429, isLocal: true, isDefinition: true, scopeLine: 188, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!429 = !DISubroutineType(types: !430)
!430 = !{!25, !431}
!431 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !48, size: 64)
!432 = !DILocation(line: 189, column: 11, scope: !428)
!433 = !DILocation(line: 190, column: 5, scope: !428)
!434 = distinct !DISubprogram(name: "xgene_ahci_is_memram_inited", scope: !3, file: !3, line: 193, type: !429, isLocal: true, isDefinition: true, scopeLine: 194, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!435 = !DILocation(line: 195, column: 11, scope: !434)
!436 = !DILocation(line: 196, column: 5, scope: !434)
!437 = distinct !DISubprogram(name: "ahci_platform_enable_clks", scope: !3, file: !3, line: 199, type: !438, isLocal: true, isDefinition: true, scopeLine: 200, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!438 = !DISubroutineType(types: !439)
!439 = !{!25, !51}
!440 = !DILocation(line: 201, column: 11, scope: !437)
!441 = !DILocation(line: 202, column: 5, scope: !437)
!442 = distinct !DISubprogram(name: "ahci_platform_disable_clks", scope: !3, file: !3, line: 205, type: !443, isLocal: true, isDefinition: true, scopeLine: 206, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!443 = !DISubroutineType(types: !444)
!444 = !{null, !51}
!445 = !DILocation(line: 207, column: 11, scope: !442)
!446 = !DILocation(line: 208, column: 1, scope: !442)
!447 = distinct !DISubprogram(name: "ahci_platform_enable_resources", scope: !3, file: !3, line: 210, type: !438, isLocal: true, isDefinition: true, scopeLine: 211, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!448 = !DILocation(line: 212, column: 11, scope: !447)
!449 = !DILocation(line: 213, column: 5, scope: !447)
!450 = distinct !DISubprogram(name: "xgene_ahci_hw_init", scope: !3, file: !3, line: 221, type: !443, isLocal: true, isDefinition: true, scopeLine: 222, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!451 = !DILocation(line: 223, column: 11, scope: !450)
!452 = !DILocation(line: 224, column: 1, scope: !450)
!453 = distinct !DISubprogram(name: "xgene_ahci_irq_intr", scope: !3, file: !3, line: 92, type: !43, isLocal: true, isDefinition: true, scopeLine: 93, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!454 = !DILocation(line: 94, column: 11, scope: !453)
!455 = !DILocation(line: 95, column: 11, scope: !453)
!456 = !DILocation(line: 96, column: 5, scope: !453)
!457 = distinct !DISubprogram(name: "ahci_platform_init_host", scope: !3, file: !3, line: 226, type: !458, isLocal: true, isDefinition: true, scopeLine: 230, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!458 = !DISubroutineType(types: !459)
!459 = !{!25, !138, !51, !460, !461}
!460 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !28, size: 64)
!461 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !104, size: 64)
!462 = !DILocation(line: 231, column: 11, scope: !457)
!463 = !DILocation(line: 232, column: 11, scope: !457)
!464 = !DILocation(line: 233, column: 11, scope: !457)
!465 = !DILocation(line: 234, column: 11, scope: !457)
!466 = !DILocation(line: 235, column: 5, scope: !457)
!467 = distinct !DISubprogram(name: "ahci_platform_disable_resources", scope: !3, file: !3, line: 216, type: !443, isLocal: true, isDefinition: true, scopeLine: 217, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !110)
!468 = !DILocation(line: 218, column: 11, scope: !467)
!469 = !DILocation(line: 219, column: 1, scope: !467)
!470 = distinct !DISubprogram(name: "memcpy", scope: !109, file: !109, line: 12, type: !471, isLocal: false, isDefinition: true, scopeLine: 12, flags: DIFlagPrototyped, isOptimized: false, unit: !108, retainedNodes: !110)
!471 = !DISubroutineType(types: !472)
!472 = !{!15, !15, !82, !473}
!473 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !474, line: 62, baseType: !11)
!474 = !DIFile(filename: "/opt/llvm7/lib/clang/7.0.0/include/stddef.h", directory: "/work/build/klee-original/runtime/FreeStanding")
!475 = !DILocation(line: 13, column: 16, scope: !470)
!476 = !DILocation(line: 13, column: 9, scope: !470)
!477 = !DILocation(line: 14, column: 21, scope: !470)
!478 = !DILocation(line: 14, column: 15, scope: !470)
!479 = !DILocation(line: 16, column: 3, scope: !470)
!480 = !DILocation(line: 16, column: 13, scope: !470)
!481 = !DILocation(line: 16, column: 16, scope: !470)
!482 = !DILocation(line: 17, column: 19, scope: !470)
!483 = !DILocation(line: 17, column: 15, scope: !470)
!484 = !DILocation(line: 17, column: 10, scope: !470)
!485 = !DILocation(line: 17, column: 13, scope: !470)
!486 = distinct !{!486, !479, !482}
!487 = !DILocation(line: 18, column: 10, scope: !470)
!488 = !DILocation(line: 18, column: 3, scope: !470)
