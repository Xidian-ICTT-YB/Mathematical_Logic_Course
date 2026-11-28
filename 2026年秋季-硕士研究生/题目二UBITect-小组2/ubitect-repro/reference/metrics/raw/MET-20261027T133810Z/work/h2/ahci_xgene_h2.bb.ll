; ModuleID = 'ahci_xgene_h2.bc'
source_filename = "ahci_xgene_h2.c"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

%struct.platform_device = type { %struct.device }
%struct.device = type { i32 }
%struct.ata_port_info = type { i32 }
%struct.of_device_id = type { i8* }
%struct.acpi_device_id = type { [16 x i8], i64 }
%struct.scsi_host_template = type { i32 }
%struct.ahci_host_priv = type { i8*, i8*, i32, i32 (i32, i8*)* }
%struct.xgene_ahci_context = type { %struct.ahci_host_priv*, %struct.device*, [2 x i8], [2 x i32], i8*, i8*, i8*, i8* }
%struct.resource = type { i32 }
%struct.acpi_device_info = type { i32, i32 }

@stub_acpi_handle = internal global i64 0, align 8, !dbg !0
@global_pdev = internal global %struct.platform_device zeroinitializer, align 4, !dbg !17
@xgene_ahci_v1_port_info = internal constant %struct.ata_port_info { i32 1 }, align 4, !dbg !26
@xgene_ahci_v2_port_info = internal constant %struct.ata_port_info { i32 2 }, align 4, !dbg !32
@xgene_ahci_probe.ppi = private unnamed_addr constant [2 x %struct.ata_port_info*] [%struct.ata_port_info* @xgene_ahci_v1_port_info, %struct.ata_port_info* @xgene_ahci_v2_port_info], align 16
@xgene_ahci_of_match = internal constant [1 x %struct.of_device_id] zeroinitializer, align 8, !dbg !75
@xgene_ahci_acpi_match = internal constant [3 x %struct.acpi_device_id] [%struct.acpi_device_id { [16 x i8] c"APMC0D0D\00\00\00\00\00\00\00\00", i64 1 }, %struct.acpi_device_id { [16 x i8] c"APMC0D32\00\00\00\00\00\00\00\00", i64 2 }, %struct.acpi_device_id zeroinitializer], align 16, !dbg !96
@.str = private unnamed_addr constant [46 x i8] c"No node entry in ACPI table. Assume version1\0A\00", align 1
@.str.1 = private unnamed_addr constant [48 x i8] c"%s: Error reading device info. Assume version1\0A\00", align 1
@__func__.xgene_ahci_probe = private unnamed_addr constant [17 x i8] c"xgene_ahci_probe\00", align 1
@.str.2 = private unnamed_addr constant [28 x i8] c"VAddr 0x%p Mmio VAddr 0x%p\0A\00", align 1
@.str.3 = private unnamed_addr constant [36 x i8] c"SATA mux selection failed error %d\0A\00", align 1
@.str.4 = private unnamed_addr constant [35 x i8] c"skip clock and PHY initialization\0A\00", align 1
@ahci_platform_sht = internal global %struct.scsi_host_template zeroinitializer, align 4, !dbg !102
@.str.5 = private unnamed_addr constant [41 x i8] c"X-Gene SATA host controller initialized\0A\00", align 1
@global_hpriv = internal global %struct.ahci_host_priv zeroinitializer, align 8, !dbg !34
@global_ctx = internal global %struct.xgene_ahci_context zeroinitializer, align 8, !dbg !46
@global_resource = internal global %struct.resource zeroinitializer, align 4, !dbg !70
@global_acpi_id = internal global %struct.acpi_device_id { [16 x i8] c"APMC0D32\00\00\00\00\00\00\00\00", i64 2 }, align 8, !dbg !86
@llvm.used = appending global [2 x i8*] [i8* bitcast (i32 (i32)* @history_entry to i8*), i8* bitcast (i32 (i32)* @history_entry_failure to i8*)], section "llvm.metadata"

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @history_entry(i32) #0 !dbg !112 {
ahci_xgene_h2.llbc-history_entry-0:
  %1 = alloca i32, align 4
  store i32 %0, i32* %1, align 4
  call void @llvm.dbg.declare(metadata i32* %1, metadata !117, metadata !DIExpression()), !dbg !118
  %2 = load i32, i32* %1, align 4, !dbg !119
  %3 = sext i32 %2 to i64, !dbg !120
  store volatile i64 %3, i64* @stub_acpi_handle, align 8, !dbg !121
  %4 = call i32 @xgene_ahci_probe(%struct.platform_device* @global_pdev), !dbg !122
  ret i32 %4, !dbg !123
}

; Function Attrs: nounwind readnone speculatable
declare void @llvm.dbg.declare(metadata, metadata, metadata) #1

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @xgene_ahci_probe(%struct.platform_device*) #0 !dbg !124 {
ahci_xgene_h2.llbc-xgene_ahci_probe-0:
  %1 = alloca i32, align 4
  %2 = alloca %struct.platform_device*, align 8
  %3 = alloca %struct.device*, align 8
  %4 = alloca %struct.ahci_host_priv*, align 8
  %5 = alloca %struct.xgene_ahci_context*, align 8
  %6 = alloca %struct.resource*, align 8
  %7 = alloca %struct.of_device_id*, align 8
  %8 = alloca i32, align 4
  %9 = alloca [2 x %struct.ata_port_info*], align 16
  %10 = alloca i32, align 4
  %11 = alloca i8*, align 8
  %12 = alloca %struct.acpi_device_id*, align 8
  %13 = alloca %struct.acpi_device_info*, align 8
  %14 = alloca i32, align 4
  store %struct.platform_device* %0, %struct.platform_device** %2, align 8
  call void @llvm.dbg.declare(metadata %struct.platform_device** %2, metadata !129, metadata !DIExpression()), !dbg !130
  call void @llvm.dbg.declare(metadata %struct.device** %3, metadata !131, metadata !DIExpression()), !dbg !132
  %15 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !133
  %16 = getelementptr inbounds %struct.platform_device, %struct.platform_device* %15, i32 0, i32 0, !dbg !134
  store %struct.device* %16, %struct.device** %3, align 8, !dbg !132
  call void @llvm.dbg.declare(metadata %struct.ahci_host_priv** %4, metadata !135, metadata !DIExpression()), !dbg !136
  call void @llvm.dbg.declare(metadata %struct.xgene_ahci_context** %5, metadata !137, metadata !DIExpression()), !dbg !139
  call void @llvm.dbg.declare(metadata %struct.resource** %6, metadata !140, metadata !DIExpression()), !dbg !142
  call void @llvm.dbg.declare(metadata %struct.of_device_id** %7, metadata !143, metadata !DIExpression()), !dbg !145
  call void @llvm.dbg.declare(metadata i32* %8, metadata !146, metadata !DIExpression()), !dbg !147
  store i32 1, i32* %8, align 4, !dbg !147
  call void @llvm.dbg.declare(metadata [2 x %struct.ata_port_info*]* %9, metadata !148, metadata !DIExpression()), !dbg !151
  %17 = bitcast [2 x %struct.ata_port_info*]* %9 to i8*, !dbg !151
  call void @llvm.memcpy.p0i8.p0i8.i64(i8* align 16 %17, i8* align 16 bitcast ([2 x %struct.ata_port_info*]* @xgene_ahci_probe.ppi to i8*), i64 16, i1 false), !dbg !151
  call void @llvm.dbg.declare(metadata i32* %10, metadata !152, metadata !DIExpression()), !dbg !153
  %18 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !154
  %19 = call %struct.ahci_host_priv* @ahci_platform_get_resources(%struct.platform_device* %18), !dbg !155
  store %struct.ahci_host_priv* %19, %struct.ahci_host_priv** %4, align 8, !dbg !156
  %20 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !157
  %21 = ptrtoint %struct.ahci_host_priv* %20 to i64, !dbg !157
  %22 = icmp uge i64 %21, -4095, !dbg !157
  br i1 %22, label %ahci_xgene_h2.llbc-xgene_ahci_probe-1, label %ahci_xgene_h2.llbc-xgene_ahci_probe-2, !dbg !159

ahci_xgene_h2.llbc-xgene_ahci_probe-1:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-0
  %23 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !160
  %24 = ptrtoint %struct.ahci_host_priv* %23 to i64, !dbg !160
  %25 = trunc i64 %24 to i32, !dbg !160
  store i32 %25, i32* %1, align 4, !dbg !161
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !161

ahci_xgene_h2.llbc-xgene_ahci_probe-2:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-0
  %26 = load %struct.device*, %struct.device** %3, align 8, !dbg !162
  %27 = call i8* @devm_kzalloc(%struct.device* %26, i64 64, i32 0), !dbg !163
  %28 = bitcast i8* %27 to %struct.xgene_ahci_context*, !dbg !163
  store %struct.xgene_ahci_context* %28, %struct.xgene_ahci_context** %5, align 8, !dbg !164
  %29 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !165
  %30 = icmp ne %struct.xgene_ahci_context* %29, null, !dbg !165
  br i1 %30, label %ahci_xgene_h2.llbc-xgene_ahci_probe-4, label %ahci_xgene_h2.llbc-xgene_ahci_probe-3, !dbg !167

ahci_xgene_h2.llbc-xgene_ahci_probe-3:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-2
  store i32 -12, i32* %1, align 4, !dbg !168
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !168

ahci_xgene_h2.llbc-xgene_ahci_probe-4:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-2
  %31 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !169
  %32 = bitcast %struct.xgene_ahci_context* %31 to i8*, !dbg !169
  %33 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !170
  %34 = getelementptr inbounds %struct.ahci_host_priv, %struct.ahci_host_priv* %33, i32 0, i32 1, !dbg !171
  store i8* %32, i8** %34, align 8, !dbg !172
  %35 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !173
  %36 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !174
  %37 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %36, i32 0, i32 0, !dbg !175
  store %struct.ahci_host_priv* %35, %struct.ahci_host_priv** %37, align 8, !dbg !176
  %38 = load %struct.device*, %struct.device** %3, align 8, !dbg !177
  %39 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !178
  %40 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %39, i32 0, i32 1, !dbg !179
  store %struct.device* %38, %struct.device** %40, align 8, !dbg !180
  %41 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !181
  %42 = call %struct.resource* @platform_get_resource(%struct.platform_device* %41, i32 512, i32 1), !dbg !182
  store %struct.resource* %42, %struct.resource** %6, align 8, !dbg !183
  %43 = load %struct.device*, %struct.device** %3, align 8, !dbg !184
  %44 = load %struct.resource*, %struct.resource** %6, align 8, !dbg !185
  %45 = call i8* @devm_ioremap_resource(%struct.device* %43, %struct.resource* %44), !dbg !186
  %46 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !187
  %47 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %46, i32 0, i32 4, !dbg !188
  store i8* %45, i8** %47, align 8, !dbg !189
  %48 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !190
  %49 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %48, i32 0, i32 4, !dbg !190
  %50 = load i8*, i8** %49, align 8, !dbg !190
  %51 = ptrtoint i8* %50 to i64, !dbg !190
  %52 = icmp uge i64 %51, -4095, !dbg !190
  br i1 %52, label %ahci_xgene_h2.llbc-xgene_ahci_probe-5, label %ahci_xgene_h2.llbc-xgene_ahci_probe-6, !dbg !192

ahci_xgene_h2.llbc-xgene_ahci_probe-5:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-4
  %53 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !193
  %54 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %53, i32 0, i32 4, !dbg !193
  %55 = load i8*, i8** %54, align 8, !dbg !193
  %56 = ptrtoint i8* %55 to i64, !dbg !193
  %57 = trunc i64 %56 to i32, !dbg !193
  store i32 %57, i32* %1, align 4, !dbg !194
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !194

ahci_xgene_h2.llbc-xgene_ahci_probe-6:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-4
  %58 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !195
  %59 = call %struct.resource* @platform_get_resource(%struct.platform_device* %58, i32 512, i32 2), !dbg !196
  store %struct.resource* %59, %struct.resource** %6, align 8, !dbg !197
  %60 = load %struct.device*, %struct.device** %3, align 8, !dbg !198
  %61 = load %struct.resource*, %struct.resource** %6, align 8, !dbg !199
  %62 = call i8* @devm_ioremap_resource(%struct.device* %60, %struct.resource* %61), !dbg !200
  %63 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !201
  %64 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %63, i32 0, i32 5, !dbg !202
  store i8* %62, i8** %64, align 8, !dbg !203
  %65 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !204
  %66 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %65, i32 0, i32 5, !dbg !204
  %67 = load i8*, i8** %66, align 8, !dbg !204
  %68 = ptrtoint i8* %67 to i64, !dbg !204
  %69 = icmp uge i64 %68, -4095, !dbg !204
  br i1 %69, label %ahci_xgene_h2.llbc-xgene_ahci_probe-7, label %ahci_xgene_h2.llbc-xgene_ahci_probe-8, !dbg !206

ahci_xgene_h2.llbc-xgene_ahci_probe-7:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-6
  %70 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !207
  %71 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %70, i32 0, i32 5, !dbg !207
  %72 = load i8*, i8** %71, align 8, !dbg !207
  %73 = ptrtoint i8* %72 to i64, !dbg !207
  %74 = trunc i64 %73 to i32, !dbg !207
  store i32 %74, i32* %1, align 4, !dbg !208
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !208

ahci_xgene_h2.llbc-xgene_ahci_probe-8:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-6
  %75 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !209
  %76 = call %struct.resource* @platform_get_resource(%struct.platform_device* %75, i32 512, i32 3), !dbg !210
  store %struct.resource* %76, %struct.resource** %6, align 8, !dbg !211
  %77 = load %struct.device*, %struct.device** %3, align 8, !dbg !212
  %78 = load %struct.resource*, %struct.resource** %6, align 8, !dbg !213
  %79 = call i8* @devm_ioremap_resource(%struct.device* %77, %struct.resource* %78), !dbg !214
  %80 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !215
  %81 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %80, i32 0, i32 6, !dbg !216
  store i8* %79, i8** %81, align 8, !dbg !217
  %82 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !218
  %83 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %82, i32 0, i32 6, !dbg !218
  %84 = load i8*, i8** %83, align 8, !dbg !218
  %85 = ptrtoint i8* %84 to i64, !dbg !218
  %86 = icmp uge i64 %85, -4095, !dbg !218
  br i1 %86, label %ahci_xgene_h2.llbc-xgene_ahci_probe-9, label %ahci_xgene_h2.llbc-xgene_ahci_probe-10, !dbg !220

ahci_xgene_h2.llbc-xgene_ahci_probe-9:            ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-8
  %87 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !221
  %88 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %87, i32 0, i32 6, !dbg !221
  %89 = load i8*, i8** %88, align 8, !dbg !221
  %90 = ptrtoint i8* %89 to i64, !dbg !221
  %91 = trunc i64 %90 to i32, !dbg !221
  store i32 %91, i32* %1, align 4, !dbg !222
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !222

ahci_xgene_h2.llbc-xgene_ahci_probe-10:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-8
  %92 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !223
  %93 = call %struct.resource* @platform_get_resource(%struct.platform_device* %92, i32 512, i32 4), !dbg !224
  store %struct.resource* %93, %struct.resource** %6, align 8, !dbg !225
  %94 = load %struct.resource*, %struct.resource** %6, align 8, !dbg !226
  %95 = icmp ne %struct.resource* %94, null, !dbg !226
  br i1 %95, label %ahci_xgene_h2.llbc-xgene_ahci_probe-11, label %ahci_xgene_h2.llbc-xgene_ahci_probe-14, !dbg !228

ahci_xgene_h2.llbc-xgene_ahci_probe-11:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-10
  call void @llvm.dbg.declare(metadata i8** %11, metadata !229, metadata !DIExpression()), !dbg !231
  %96 = load %struct.device*, %struct.device** %3, align 8, !dbg !232
  %97 = load %struct.resource*, %struct.resource** %6, align 8, !dbg !233
  %98 = call i8* @devm_ioremap_resource(%struct.device* %96, %struct.resource* %97), !dbg !234
  store i8* %98, i8** %11, align 8, !dbg !231
  %99 = load i8*, i8** %11, align 8, !dbg !235
  %100 = ptrtoint i8* %99 to i64, !dbg !235
  %101 = icmp uge i64 %100, -4095, !dbg !235
  br i1 %101, label %ahci_xgene_h2.llbc-xgene_ahci_probe-12, label %ahci_xgene_h2.llbc-xgene_ahci_probe-13, !dbg !237

ahci_xgene_h2.llbc-xgene_ahci_probe-12:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-11
  %102 = load i8*, i8** %11, align 8, !dbg !238
  %103 = ptrtoint i8* %102 to i64, !dbg !238
  %104 = trunc i64 %103 to i32, !dbg !238
  store i32 %104, i32* %1, align 4, !dbg !239
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !239

ahci_xgene_h2.llbc-xgene_ahci_probe-13:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-11
  %105 = load i8*, i8** %11, align 8, !dbg !240
  %106 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !241
  %107 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %106, i32 0, i32 7, !dbg !242
  store i8* %105, i8** %107, align 8, !dbg !243
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-14, !dbg !244

ahci_xgene_h2.llbc-xgene_ahci_probe-14:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-13, %ahci_xgene_h2.llbc-xgene_ahci_probe-10
  %108 = load %struct.device*, %struct.device** %3, align 8, !dbg !245
  %109 = call %struct.of_device_id* @of_match_device(%struct.of_device_id* getelementptr inbounds ([1 x %struct.of_device_id], [1 x %struct.of_device_id]* @xgene_ahci_of_match, i32 0, i32 0), %struct.device* %108), !dbg !246
  store %struct.of_device_id* %109, %struct.of_device_id** %7, align 8, !dbg !247
  %110 = load %struct.of_device_id*, %struct.of_device_id** %7, align 8, !dbg !248
  %111 = icmp ne %struct.of_device_id* %110, null, !dbg !248
  br i1 %111, label %ahci_xgene_h2.llbc-xgene_ahci_probe-15, label %ahci_xgene_h2.llbc-xgene_ahci_probe-18, !dbg !250

ahci_xgene_h2.llbc-xgene_ahci_probe-15:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-14
  %112 = load %struct.of_device_id*, %struct.of_device_id** %7, align 8, !dbg !251
  %113 = getelementptr inbounds %struct.of_device_id, %struct.of_device_id* %112, i32 0, i32 0, !dbg !254
  %114 = load i8*, i8** %113, align 8, !dbg !254
  %115 = icmp ne i8* %114, null, !dbg !251
  br i1 %115, label %ahci_xgene_h2.llbc-xgene_ahci_probe-16, label %ahci_xgene_h2.llbc-xgene_ahci_probe-17, !dbg !255

ahci_xgene_h2.llbc-xgene_ahci_probe-16:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-15
  %116 = load %struct.of_device_id*, %struct.of_device_id** %7, align 8, !dbg !256
  %117 = getelementptr inbounds %struct.of_device_id, %struct.of_device_id* %116, i32 0, i32 0, !dbg !257
  %118 = load i8*, i8** %117, align 8, !dbg !257
  %119 = ptrtoint i8* %118 to i32, !dbg !258
  store i32 %119, i32* %8, align 4, !dbg !259
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-17, !dbg !260

ahci_xgene_h2.llbc-xgene_ahci_probe-17:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-16, %ahci_xgene_h2.llbc-xgene_ahci_probe-15
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-29, !dbg !261

ahci_xgene_h2.llbc-xgene_ahci_probe-18:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-14
  call void @llvm.dbg.declare(metadata %struct.acpi_device_id** %12, metadata !262, metadata !DIExpression()), !dbg !265
  call void @llvm.dbg.declare(metadata %struct.acpi_device_info** %13, metadata !266, metadata !DIExpression()), !dbg !272
  call void @llvm.dbg.declare(metadata i32* %14, metadata !273, metadata !DIExpression()), !dbg !275
  %120 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !276
  %121 = getelementptr inbounds %struct.platform_device, %struct.platform_device* %120, i32 0, i32 0, !dbg !277
  %122 = call %struct.acpi_device_id* @acpi_match_device(%struct.acpi_device_id* getelementptr inbounds ([3 x %struct.acpi_device_id], [3 x %struct.acpi_device_id]* @xgene_ahci_acpi_match, i32 0, i32 0), %struct.device* %121), !dbg !278
  store %struct.acpi_device_id* %122, %struct.acpi_device_id** %12, align 8, !dbg !279
  %123 = load %struct.acpi_device_id*, %struct.acpi_device_id** %12, align 8, !dbg !280
  %124 = icmp ne %struct.acpi_device_id* %123, null, !dbg !280
  br i1 %124, label %ahci_xgene_h2.llbc-xgene_ahci_probe-20, label %ahci_xgene_h2.llbc-xgene_ahci_probe-19, !dbg !282

ahci_xgene_h2.llbc-xgene_ahci_probe-19:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-18
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([46 x i8], [46 x i8]* @.str, i32 0, i32 0)), !dbg !283
  store i32 1, i32* %8, align 4, !dbg !285
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-28, !dbg !286

ahci_xgene_h2.llbc-xgene_ahci_probe-20:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-18
  %125 = load %struct.acpi_device_id*, %struct.acpi_device_id** %12, align 8, !dbg !287
  %126 = getelementptr inbounds %struct.acpi_device_id, %struct.acpi_device_id* %125, i32 0, i32 1, !dbg !289
  %127 = load i64, i64* %126, align 8, !dbg !289
  %128 = icmp ne i64 %127, 0, !dbg !287
  br i1 %128, label %ahci_xgene_h2.llbc-xgene_ahci_probe-21, label %ahci_xgene_h2.llbc-xgene_ahci_probe-27, !dbg !290

ahci_xgene_h2.llbc-xgene_ahci_probe-21:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-20
  %129 = load %struct.acpi_device_id*, %struct.acpi_device_id** %12, align 8, !dbg !291
  %130 = getelementptr inbounds %struct.acpi_device_id, %struct.acpi_device_id* %129, i32 0, i32 1, !dbg !293
  %131 = load i64, i64* %130, align 8, !dbg !293
  %132 = trunc i64 %131 to i32, !dbg !294
  store i32 %132, i32* %8, align 4, !dbg !295
  %133 = load volatile i64, i64* @stub_acpi_handle, align 8, !dbg !296
  %134 = call i32 @acpi_get_object_info(i64 %133, %struct.acpi_device_info** %13), !dbg !297
  store i32 %134, i32* %14, align 4, !dbg !298
  %135 = load i32, i32* %14, align 4, !dbg !299
  %136 = icmp ne i32 %135, 0, !dbg !299
  br i1 %136, label %ahci_xgene_h2.llbc-xgene_ahci_probe-22, label %ahci_xgene_h2.llbc-xgene_ahci_probe-23, !dbg !301

ahci_xgene_h2.llbc-xgene_ahci_probe-22:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-21
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([48 x i8], [48 x i8]* @.str.1, i32 0, i32 0), i8* getelementptr inbounds ([17 x i8], [17 x i8]* @__func__.xgene_ahci_probe, i32 0, i32 0)), !dbg !302
  store i32 1, i32* %8, align 4, !dbg !304
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-26, !dbg !305

ahci_xgene_h2.llbc-xgene_ahci_probe-23:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-21
  %137 = load %struct.acpi_device_info*, %struct.acpi_device_info** %13, align 8, !dbg !306
  %138 = getelementptr inbounds %struct.acpi_device_info, %struct.acpi_device_info* %137, i32 0, i32 0, !dbg !308
  %139 = load i32, i32* %138, align 4, !dbg !308
  %140 = and i32 %139, 1, !dbg !309
  %141 = icmp ne i32 %140, 0, !dbg !309
  br i1 %141, label %ahci_xgene_h2.llbc-xgene_ahci_probe-24, label %ahci_xgene_h2.llbc-xgene_ahci_probe-25, !dbg !310

ahci_xgene_h2.llbc-xgene_ahci_probe-24:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-23
  store i32 2, i32* %8, align 4, !dbg !311
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-25, !dbg !313

ahci_xgene_h2.llbc-xgene_ahci_probe-25:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-24, %ahci_xgene_h2.llbc-xgene_ahci_probe-23
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-26

ahci_xgene_h2.llbc-xgene_ahci_probe-26:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-25, %ahci_xgene_h2.llbc-xgene_ahci_probe-22
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-27, !dbg !314

ahci_xgene_h2.llbc-xgene_ahci_probe-27:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-26, %ahci_xgene_h2.llbc-xgene_ahci_probe-20
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-28

ahci_xgene_h2.llbc-xgene_ahci_probe-28:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-27, %ahci_xgene_h2.llbc-xgene_ahci_probe-19
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-29

ahci_xgene_h2.llbc-xgene_ahci_probe-29:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-28, %ahci_xgene_h2.llbc-xgene_ahci_probe-17
  %142 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !315
  %143 = getelementptr inbounds %struct.xgene_ahci_context, %struct.xgene_ahci_context* %142, i32 0, i32 4, !dbg !315
  %144 = load i8*, i8** %143, align 8, !dbg !315
  %145 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !315
  %146 = getelementptr inbounds %struct.ahci_host_priv, %struct.ahci_host_priv* %145, i32 0, i32 0, !dbg !315
  %147 = load i8*, i8** %146, align 8, !dbg !315
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([28 x i8], [28 x i8]* @.str.2, i32 0, i32 0), i8* %144, i8* %147), !dbg !315
  %148 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !316
  %149 = call i32 @xgene_ahci_mux_select(%struct.xgene_ahci_context* %148), !dbg !318
  store i32 %149, i32* %10, align 4, !dbg !319
  %150 = icmp ne i32 %149, 0, !dbg !319
  br i1 %150, label %ahci_xgene_h2.llbc-xgene_ahci_probe-30, label %ahci_xgene_h2.llbc-xgene_ahci_probe-31, !dbg !320

ahci_xgene_h2.llbc-xgene_ahci_probe-30:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-29
  %151 = load i32, i32* %10, align 4, !dbg !321
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([36 x i8], [36 x i8]* @.str.3, i32 0, i32 0), i32 %151), !dbg !321
  store i32 -19, i32* %1, align 4, !dbg !323
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !323

ahci_xgene_h2.llbc-xgene_ahci_probe-31:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-29
  %152 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %5, align 8, !dbg !324
  %153 = call i32 @xgene_ahci_is_memram_inited(%struct.xgene_ahci_context* %152), !dbg !326
  %154 = icmp ne i32 %153, 0, !dbg !326
  br i1 %154, label %ahci_xgene_h2.llbc-xgene_ahci_probe-32, label %ahci_xgene_h2.llbc-xgene_ahci_probe-33, !dbg !327

ahci_xgene_h2.llbc-xgene_ahci_probe-32:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-31
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([35 x i8], [35 x i8]* @.str.4, i32 0, i32 0)), !dbg !328
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-38, !dbg !330

ahci_xgene_h2.llbc-xgene_ahci_probe-33:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-31
  %155 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !331
  %156 = call i32 @ahci_platform_enable_clks(%struct.ahci_host_priv* %155), !dbg !332
  store i32 %156, i32* %10, align 4, !dbg !333
  %157 = load i32, i32* %10, align 4, !dbg !334
  %158 = icmp ne i32 %157, 0, !dbg !334
  br i1 %158, label %ahci_xgene_h2.llbc-xgene_ahci_probe-34, label %ahci_xgene_h2.llbc-xgene_ahci_probe-35, !dbg !336

ahci_xgene_h2.llbc-xgene_ahci_probe-34:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-33
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-45, !dbg !337

ahci_xgene_h2.llbc-xgene_ahci_probe-35:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-33
  %159 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !338
  call void @ahci_platform_disable_clks(%struct.ahci_host_priv* %159), !dbg !339
  %160 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !340
  %161 = call i32 @ahci_platform_enable_resources(%struct.ahci_host_priv* %160), !dbg !341
  store i32 %161, i32* %10, align 4, !dbg !342
  %162 = load i32, i32* %10, align 4, !dbg !343
  %163 = icmp ne i32 %162, 0, !dbg !343
  br i1 %163, label %ahci_xgene_h2.llbc-xgene_ahci_probe-36, label %ahci_xgene_h2.llbc-xgene_ahci_probe-37, !dbg !345

ahci_xgene_h2.llbc-xgene_ahci_probe-36:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-35
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-45, !dbg !346

ahci_xgene_h2.llbc-xgene_ahci_probe-37:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-35
  %164 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !347
  call void @xgene_ahci_hw_init(%struct.ahci_host_priv* %164), !dbg !348
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-38, !dbg !348

ahci_xgene_h2.llbc-xgene_ahci_probe-38:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-37, %ahci_xgene_h2.llbc-xgene_ahci_probe-32
  %165 = load i32, i32* %8, align 4, !dbg !349
  switch i32 %165, label %ahci_xgene_h2.llbc-xgene_ahci_probe-41 [
    i32 1, label %ahci_xgene_h2.llbc-xgene_ahci_probe-39
    i32 2, label %ahci_xgene_h2.llbc-xgene_ahci_probe-40
  ], !dbg !350

ahci_xgene_h2.llbc-xgene_ahci_probe-39:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-38
  %166 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !351
  %167 = getelementptr inbounds %struct.ahci_host_priv, %struct.ahci_host_priv* %166, i32 0, i32 2, !dbg !353
  store i32 2, i32* %167, align 8, !dbg !354
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-42, !dbg !355

ahci_xgene_h2.llbc-xgene_ahci_probe-40:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-38
  %168 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !356
  %169 = getelementptr inbounds %struct.ahci_host_priv, %struct.ahci_host_priv* %168, i32 0, i32 2, !dbg !357
  %170 = load i32, i32* %169, align 8, !dbg !358
  %171 = or i32 %170, 4, !dbg !358
  store i32 %171, i32* %169, align 8, !dbg !358
  %172 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !359
  %173 = getelementptr inbounds %struct.ahci_host_priv, %struct.ahci_host_priv* %172, i32 0, i32 3, !dbg !360
  store i32 (i32, i8*)* @xgene_ahci_irq_intr, i32 (i32, i8*)** %173, align 8, !dbg !361
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-42, !dbg !362

ahci_xgene_h2.llbc-xgene_ahci_probe-41:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-38
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-42, !dbg !363

ahci_xgene_h2.llbc-xgene_ahci_probe-42:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-41, %ahci_xgene_h2.llbc-xgene_ahci_probe-40, %ahci_xgene_h2.llbc-xgene_ahci_probe-39
  %174 = load %struct.platform_device*, %struct.platform_device** %2, align 8, !dbg !364
  %175 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !365
  %176 = load i32, i32* %8, align 4, !dbg !366
  %177 = sub i32 %176, 1, !dbg !367
  %178 = zext i32 %177 to i64, !dbg !368
  %179 = getelementptr inbounds [2 x %struct.ata_port_info*], [2 x %struct.ata_port_info*]* %9, i64 0, i64 %178, !dbg !368
  %180 = load %struct.ata_port_info*, %struct.ata_port_info** %179, align 8, !dbg !368
  %181 = call i32 @ahci_platform_init_host(%struct.platform_device* %174, %struct.ahci_host_priv* %175, %struct.ata_port_info* %180, %struct.scsi_host_template* @ahci_platform_sht), !dbg !369
  store i32 %181, i32* %10, align 4, !dbg !370
  %182 = load i32, i32* %10, align 4, !dbg !371
  %183 = icmp ne i32 %182, 0, !dbg !371
  br i1 %183, label %ahci_xgene_h2.llbc-xgene_ahci_probe-43, label %ahci_xgene_h2.llbc-xgene_ahci_probe-44, !dbg !373

ahci_xgene_h2.llbc-xgene_ahci_probe-43:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-42
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-45, !dbg !374

ahci_xgene_h2.llbc-xgene_ahci_probe-44:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-42
  call void (i8*, ...) @stub_log(i8* getelementptr inbounds ([41 x i8], [41 x i8]* @.str.5, i32 0, i32 0)), !dbg !375
  store i32 0, i32* %1, align 4, !dbg !376
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !376

ahci_xgene_h2.llbc-xgene_ahci_probe-45:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-43, %ahci_xgene_h2.llbc-xgene_ahci_probe-36, %ahci_xgene_h2.llbc-xgene_ahci_probe-34
  %184 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %4, align 8, !dbg !377
  call void @ahci_platform_disable_resources(%struct.ahci_host_priv* %184), !dbg !378
  %185 = load i32, i32* %10, align 4, !dbg !379
  store i32 %185, i32* %1, align 4, !dbg !380
  br label %ahci_xgene_h2.llbc-xgene_ahci_probe-46, !dbg !380

ahci_xgene_h2.llbc-xgene_ahci_probe-46:           ; preds = %ahci_xgene_h2.llbc-xgene_ahci_probe-45, %ahci_xgene_h2.llbc-xgene_ahci_probe-44, %ahci_xgene_h2.llbc-xgene_ahci_probe-30, %ahci_xgene_h2.llbc-xgene_ahci_probe-12, %ahci_xgene_h2.llbc-xgene_ahci_probe-9, %ahci_xgene_h2.llbc-xgene_ahci_probe-7, %ahci_xgene_h2.llbc-xgene_ahci_probe-5, %ahci_xgene_h2.llbc-xgene_ahci_probe-3, %ahci_xgene_h2.llbc-xgene_ahci_probe-1
  %186 = load i32, i32* %1, align 4, !dbg !381
  ret i32 %186, !dbg !381
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @history_entry_failure(i32) #0 !dbg !382 {
ahci_xgene_h2.llbc-history_entry_failure-0:
  %1 = alloca i32, align 4
  %2 = alloca i32, align 4
  store i32 %0, i32* %2, align 4
  call void @llvm.dbg.declare(metadata i32* %2, metadata !383, metadata !DIExpression()), !dbg !384
  %3 = load i32, i32* %2, align 4, !dbg !385
  %4 = icmp ne i32 %3, 0, !dbg !387
  br i1 %4, label %ahci_xgene_h2.llbc-history_entry_failure-1, label %ahci_xgene_h2.llbc-history_entry_failure-2, !dbg !388

ahci_xgene_h2.llbc-history_entry_failure-1:       ; preds = %ahci_xgene_h2.llbc-history_entry_failure-0
  store i32 0, i32* %1, align 4, !dbg !389
  br label %ahci_xgene_h2.llbc-history_entry_failure-3, !dbg !389

ahci_xgene_h2.llbc-history_entry_failure-2:       ; preds = %ahci_xgene_h2.llbc-history_entry_failure-0
  store volatile i64 0, i64* @stub_acpi_handle, align 8, !dbg !390
  %5 = call i32 @xgene_ahci_probe(%struct.platform_device* @global_pdev), !dbg !391
  store i32 %5, i32* %1, align 4, !dbg !392
  br label %ahci_xgene_h2.llbc-history_entry_failure-3, !dbg !392

ahci_xgene_h2.llbc-history_entry_failure-3:       ; preds = %ahci_xgene_h2.llbc-history_entry_failure-2, %ahci_xgene_h2.llbc-history_entry_failure-1
  %6 = load i32, i32* %1, align 4, !dbg !393
  ret i32 %6, !dbg !393
}

; Function Attrs: argmemonly nounwind
declare void @llvm.memcpy.p0i8.p0i8.i64(i8* nocapture writeonly, i8* nocapture readonly, i64, i1) #2

; Function Attrs: noinline nounwind optnone uwtable
define internal %struct.ahci_host_priv* @ahci_platform_get_resources(%struct.platform_device*) #0 !dbg !394 {
ahci_xgene_h2.llbc-ahci_platform_get_resources-0:
  %1 = alloca %struct.platform_device*, align 8
  store %struct.platform_device* %0, %struct.platform_device** %1, align 8
  call void @llvm.dbg.declare(metadata %struct.platform_device** %1, metadata !397, metadata !DIExpression()), !dbg !398
  %2 = load %struct.platform_device*, %struct.platform_device** %1, align 8, !dbg !399
  ret %struct.ahci_host_priv* @global_hpriv, !dbg !400
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i8* @devm_kzalloc(%struct.device*, i64, i32) #0 !dbg !401 {
ahci_xgene_h2.llbc-devm_kzalloc-0:
  %3 = alloca %struct.device*, align 8
  %4 = alloca i64, align 8
  %5 = alloca i32, align 4
  store %struct.device* %0, %struct.device** %3, align 8
  call void @llvm.dbg.declare(metadata %struct.device** %3, metadata !406, metadata !DIExpression()), !dbg !407
  store i64 %1, i64* %4, align 8
  call void @llvm.dbg.declare(metadata i64* %4, metadata !408, metadata !DIExpression()), !dbg !409
  store i32 %2, i32* %5, align 4
  call void @llvm.dbg.declare(metadata i32* %5, metadata !410, metadata !DIExpression()), !dbg !411
  %6 = load %struct.device*, %struct.device** %3, align 8, !dbg !412
  %7 = load i64, i64* %4, align 8, !dbg !413
  %8 = load i32, i32* %5, align 4, !dbg !414
  ret i8* bitcast (%struct.xgene_ahci_context* @global_ctx to i8*), !dbg !415
}

; Function Attrs: noinline nounwind optnone uwtable
define internal %struct.resource* @platform_get_resource(%struct.platform_device*, i32, i32) #0 !dbg !416 {
ahci_xgene_h2.llbc-platform_get_resource-0:
  %3 = alloca %struct.resource*, align 8
  %4 = alloca %struct.platform_device*, align 8
  %5 = alloca i32, align 4
  %6 = alloca i32, align 4
  store %struct.platform_device* %0, %struct.platform_device** %4, align 8
  call void @llvm.dbg.declare(metadata %struct.platform_device** %4, metadata !419, metadata !DIExpression()), !dbg !420
  store i32 %1, i32* %5, align 4
  call void @llvm.dbg.declare(metadata i32* %5, metadata !421, metadata !DIExpression()), !dbg !422
  store i32 %2, i32* %6, align 4
  call void @llvm.dbg.declare(metadata i32* %6, metadata !423, metadata !DIExpression()), !dbg !424
  %7 = load %struct.platform_device*, %struct.platform_device** %4, align 8, !dbg !425
  %8 = load i32, i32* %5, align 4, !dbg !426
  %9 = load i32, i32* %6, align 4, !dbg !427
  %10 = icmp eq i32 %9, 4, !dbg !429
  br i1 %10, label %ahci_xgene_h2.llbc-platform_get_resource-1, label %ahci_xgene_h2.llbc-platform_get_resource-2, !dbg !430

ahci_xgene_h2.llbc-platform_get_resource-1:       ; preds = %ahci_xgene_h2.llbc-platform_get_resource-0
  store %struct.resource* null, %struct.resource** %3, align 8, !dbg !431
  br label %ahci_xgene_h2.llbc-platform_get_resource-3, !dbg !431

ahci_xgene_h2.llbc-platform_get_resource-2:       ; preds = %ahci_xgene_h2.llbc-platform_get_resource-0
  store %struct.resource* @global_resource, %struct.resource** %3, align 8, !dbg !432
  br label %ahci_xgene_h2.llbc-platform_get_resource-3, !dbg !432

ahci_xgene_h2.llbc-platform_get_resource-3:       ; preds = %ahci_xgene_h2.llbc-platform_get_resource-2, %ahci_xgene_h2.llbc-platform_get_resource-1
  %11 = load %struct.resource*, %struct.resource** %3, align 8, !dbg !433
  ret %struct.resource* %11, !dbg !433
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i8* @devm_ioremap_resource(%struct.device*, %struct.resource*) #0 !dbg !434 {
ahci_xgene_h2.llbc-devm_ioremap_resource-0:
  %2 = alloca %struct.device*, align 8
  %3 = alloca %struct.resource*, align 8
  store %struct.device* %0, %struct.device** %2, align 8
  call void @llvm.dbg.declare(metadata %struct.device** %2, metadata !437, metadata !DIExpression()), !dbg !438
  store %struct.resource* %1, %struct.resource** %3, align 8
  call void @llvm.dbg.declare(metadata %struct.resource** %3, metadata !439, metadata !DIExpression()), !dbg !440
  %4 = load %struct.device*, %struct.device** %2, align 8, !dbg !441
  %5 = load %struct.resource*, %struct.resource** %3, align 8, !dbg !442
  ret i8* inttoptr (i64 4096 to i8*), !dbg !443
}

; Function Attrs: noinline nounwind optnone uwtable
define internal %struct.of_device_id* @of_match_device(%struct.of_device_id*, %struct.device*) #0 !dbg !444 {
ahci_xgene_h2.llbc-of_match_device-0:
  %2 = alloca %struct.of_device_id*, align 8
  %3 = alloca %struct.device*, align 8
  store %struct.of_device_id* %0, %struct.of_device_id** %2, align 8
  call void @llvm.dbg.declare(metadata %struct.of_device_id** %2, metadata !449, metadata !DIExpression()), !dbg !450
  store %struct.device* %1, %struct.device** %3, align 8
  call void @llvm.dbg.declare(metadata %struct.device** %3, metadata !451, metadata !DIExpression()), !dbg !452
  %4 = load %struct.of_device_id*, %struct.of_device_id** %2, align 8, !dbg !453
  %5 = load %struct.device*, %struct.device** %3, align 8, !dbg !454
  ret %struct.of_device_id* null, !dbg !455
}

; Function Attrs: noinline nounwind optnone uwtable
define internal %struct.acpi_device_id* @acpi_match_device(%struct.acpi_device_id*, %struct.device*) #0 !dbg !456 {
ahci_xgene_h2.llbc-acpi_match_device-0:
  %2 = alloca %struct.acpi_device_id*, align 8
  %3 = alloca %struct.device*, align 8
  store %struct.acpi_device_id* %0, %struct.acpi_device_id** %2, align 8
  call void @llvm.dbg.declare(metadata %struct.acpi_device_id** %2, metadata !459, metadata !DIExpression()), !dbg !460
  store %struct.device* %1, %struct.device** %3, align 8
  call void @llvm.dbg.declare(metadata %struct.device** %3, metadata !461, metadata !DIExpression()), !dbg !462
  %4 = load %struct.acpi_device_id*, %struct.acpi_device_id** %2, align 8, !dbg !463
  %5 = load %struct.device*, %struct.device** %3, align 8, !dbg !464
  ret %struct.acpi_device_id* @global_acpi_id, !dbg !465
}

; Function Attrs: noinline nounwind optnone uwtable
define internal void @stub_log(i8*, ...) #0 !dbg !466 {
ahci_xgene_h2.llbc-stub_log-0:
  %1 = alloca i8*, align 8
  store i8* %0, i8** %1, align 8
  call void @llvm.dbg.declare(metadata i8** %1, metadata !471, metadata !DIExpression()), !dbg !472
  %2 = load i8*, i8** %1, align 8, !dbg !473
  ret void, !dbg !474
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @acpi_get_object_info(i64, %struct.acpi_device_info**) #0 !dbg !475 {
ahci_xgene_h2.llbc-acpi_get_object_info-0:
  %2 = alloca i64, align 8
  %3 = alloca %struct.acpi_device_info**, align 8
  store i64 %0, i64* %2, align 8
  call void @llvm.dbg.declare(metadata i64* %2, metadata !480, metadata !DIExpression()), !dbg !481
  store %struct.acpi_device_info** %1, %struct.acpi_device_info*** %3, align 8
  call void @llvm.dbg.declare(metadata %struct.acpi_device_info*** %3, metadata !482, metadata !DIExpression()), !dbg !483
  %4 = load i64, i64* %2, align 8, !dbg !484
  %5 = load %struct.acpi_device_info**, %struct.acpi_device_info*** %3, align 8, !dbg !485
  ret i32 1, !dbg !486
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @xgene_ahci_mux_select(%struct.xgene_ahci_context*) #0 !dbg !487 {
ahci_xgene_h2.llbc-xgene_ahci_mux_select-0:
  %1 = alloca %struct.xgene_ahci_context*, align 8
  store %struct.xgene_ahci_context* %0, %struct.xgene_ahci_context** %1, align 8
  call void @llvm.dbg.declare(metadata %struct.xgene_ahci_context** %1, metadata !490, metadata !DIExpression()), !dbg !491
  %2 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %1, align 8, !dbg !492
  ret i32 0, !dbg !493
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @xgene_ahci_is_memram_inited(%struct.xgene_ahci_context*) #0 !dbg !494 {
ahci_xgene_h2.llbc-xgene_ahci_is_memram_inited-0:
  %1 = alloca %struct.xgene_ahci_context*, align 8
  store %struct.xgene_ahci_context* %0, %struct.xgene_ahci_context** %1, align 8
  call void @llvm.dbg.declare(metadata %struct.xgene_ahci_context** %1, metadata !495, metadata !DIExpression()), !dbg !496
  %2 = load %struct.xgene_ahci_context*, %struct.xgene_ahci_context** %1, align 8, !dbg !497
  ret i32 1, !dbg !498
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @ahci_platform_enable_clks(%struct.ahci_host_priv*) #0 !dbg !499 {
ahci_xgene_h2.llbc-ahci_platform_enable_clks-0:
  %1 = alloca %struct.ahci_host_priv*, align 8
  store %struct.ahci_host_priv* %0, %struct.ahci_host_priv** %1, align 8
  call void @llvm.dbg.declare(metadata %struct.ahci_host_priv** %1, metadata !502, metadata !DIExpression()), !dbg !503
  %2 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %1, align 8, !dbg !504
  ret i32 0, !dbg !505
}

; Function Attrs: noinline nounwind optnone uwtable
define internal void @ahci_platform_disable_clks(%struct.ahci_host_priv*) #0 !dbg !506 {
ahci_xgene_h2.llbc-ahci_platform_disable_clks-0:
  %1 = alloca %struct.ahci_host_priv*, align 8
  store %struct.ahci_host_priv* %0, %struct.ahci_host_priv** %1, align 8
  call void @llvm.dbg.declare(metadata %struct.ahci_host_priv** %1, metadata !509, metadata !DIExpression()), !dbg !510
  %2 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %1, align 8, !dbg !511
  ret void, !dbg !512
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @ahci_platform_enable_resources(%struct.ahci_host_priv*) #0 !dbg !513 {
ahci_xgene_h2.llbc-ahci_platform_enable_resources-0:
  %1 = alloca %struct.ahci_host_priv*, align 8
  store %struct.ahci_host_priv* %0, %struct.ahci_host_priv** %1, align 8
  call void @llvm.dbg.declare(metadata %struct.ahci_host_priv** %1, metadata !514, metadata !DIExpression()), !dbg !515
  %2 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %1, align 8, !dbg !516
  ret i32 0, !dbg !517
}

; Function Attrs: noinline nounwind optnone uwtable
define internal void @xgene_ahci_hw_init(%struct.ahci_host_priv*) #0 !dbg !518 {
ahci_xgene_h2.llbc-xgene_ahci_hw_init-0:
  %1 = alloca %struct.ahci_host_priv*, align 8
  store %struct.ahci_host_priv* %0, %struct.ahci_host_priv** %1, align 8
  call void @llvm.dbg.declare(metadata %struct.ahci_host_priv** %1, metadata !519, metadata !DIExpression()), !dbg !520
  %2 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %1, align 8, !dbg !521
  ret void, !dbg !522
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @xgene_ahci_irq_intr(i32, i8*) #0 !dbg !523 {
ahci_xgene_h2.llbc-xgene_ahci_irq_intr-0:
  %2 = alloca i32, align 4
  %3 = alloca i8*, align 8
  store i32 %0, i32* %2, align 4
  call void @llvm.dbg.declare(metadata i32* %2, metadata !524, metadata !DIExpression()), !dbg !525
  store i8* %1, i8** %3, align 8
  call void @llvm.dbg.declare(metadata i8** %3, metadata !526, metadata !DIExpression()), !dbg !527
  %4 = load i32, i32* %2, align 4, !dbg !528
  %5 = load i8*, i8** %3, align 8, !dbg !529
  ret i32 0, !dbg !530
}

; Function Attrs: noinline nounwind optnone uwtable
define internal i32 @ahci_platform_init_host(%struct.platform_device*, %struct.ahci_host_priv*, %struct.ata_port_info*, %struct.scsi_host_template*) #0 !dbg !531 {
ahci_xgene_h2.llbc-ahci_platform_init_host-0:
  %4 = alloca %struct.platform_device*, align 8
  %5 = alloca %struct.ahci_host_priv*, align 8
  %6 = alloca %struct.ata_port_info*, align 8
  %7 = alloca %struct.scsi_host_template*, align 8
  store %struct.platform_device* %0, %struct.platform_device** %4, align 8
  call void @llvm.dbg.declare(metadata %struct.platform_device** %4, metadata !535, metadata !DIExpression()), !dbg !536
  store %struct.ahci_host_priv* %1, %struct.ahci_host_priv** %5, align 8
  call void @llvm.dbg.declare(metadata %struct.ahci_host_priv** %5, metadata !537, metadata !DIExpression()), !dbg !538
  store %struct.ata_port_info* %2, %struct.ata_port_info** %6, align 8
  call void @llvm.dbg.declare(metadata %struct.ata_port_info** %6, metadata !539, metadata !DIExpression()), !dbg !540
  store %struct.scsi_host_template* %3, %struct.scsi_host_template** %7, align 8
  call void @llvm.dbg.declare(metadata %struct.scsi_host_template** %7, metadata !541, metadata !DIExpression()), !dbg !542
  %8 = load %struct.platform_device*, %struct.platform_device** %4, align 8, !dbg !543
  %9 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %5, align 8, !dbg !544
  %10 = load %struct.ata_port_info*, %struct.ata_port_info** %6, align 8, !dbg !545
  %11 = load %struct.scsi_host_template*, %struct.scsi_host_template** %7, align 8, !dbg !546
  ret i32 0, !dbg !547
}

; Function Attrs: noinline nounwind optnone uwtable
define internal void @ahci_platform_disable_resources(%struct.ahci_host_priv*) #0 !dbg !548 {
ahci_xgene_h2.llbc-ahci_platform_disable_resources-0:
  %1 = alloca %struct.ahci_host_priv*, align 8
  store %struct.ahci_host_priv* %0, %struct.ahci_host_priv** %1, align 8
  call void @llvm.dbg.declare(metadata %struct.ahci_host_priv** %1, metadata !549, metadata !DIExpression()), !dbg !550
  %2 = load %struct.ahci_host_priv*, %struct.ahci_host_priv** %1, align 8, !dbg !551
  ret void, !dbg !552
}

attributes #0 = { noinline nounwind optnone uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { nounwind readnone speculatable }
attributes #2 = { argmemonly nounwind }

!llvm.dbg.cu = !{!2}
!llvm.module.flags = !{!108, !109, !110}
!llvm.ident = !{!111}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(name: "stub_acpi_handle", scope: !2, file: !3, line: 90, type: !107, isLocal: true, isDefinition: true)
!2 = distinct !DICompileUnit(language: DW_LANG_C99, file: !3, producer: "clang version 7.0.0 (tags/RELEASE_700/final)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, enums: !4, retainedTypes: !10, globals: !16)
!3 = !DIFile(filename: "ahci_xgene_h2.c", directory: "/work/history/ahci_xgene/runs/HIST-20261027T133810Z/h2")
!4 = !{!5}
!5 = !DICompositeType(tag: DW_TAG_enumeration_type, name: "xgene_ahci_version", file: !3, line: 68, baseType: !6, size: 32, elements: !7)
!6 = !DIBasicType(name: "unsigned int", size: 32, encoding: DW_ATE_unsigned)
!7 = !{!8, !9}
!8 = !DIEnumerator(name: "XGENE_AHCI_V1", value: 1, isUnsigned: true)
!9 = !DIEnumerator(name: "XGENE_AHCI_V2", value: 2, isUnsigned: true)
!10 = !{!11, !12, !14, !5, !15}
!11 = !DIBasicType(name: "long unsigned int", size: 64, encoding: DW_ATE_unsigned)
!12 = !DIDerivedType(tag: DW_TAG_typedef, name: "uintptr_t", file: !13, line: 79, baseType: !11)
!13 = !DIFile(filename: "/usr/include/stdint.h", directory: "/work/history/ahci_xgene/runs/HIST-20261027T133810Z/h2")
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
!63 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/stdint-uintn.h", directory: "/work/history/ahci_xgene/runs/HIST-20261027T133810Z/h2")
!64 = !DIDerivedType(tag: DW_TAG_typedef, name: "__uint32_t", file: !65, line: 42, baseType: !6)
!65 = !DIFile(filename: "/usr/include/x86_64-linux-gnu/bits/types.h", directory: "/work/history/ahci_xgene/runs/HIST-20261027T133810Z/h2")
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
!108 = !{i32 2, !"Dwarf Version", i32 4}
!109 = !{i32 2, !"Debug Info Version", i32 3}
!110 = !{i32 1, !"wchar_size", i32 4}
!111 = !{!"clang version 7.0.0 (tags/RELEASE_700/final)"}
!112 = distinct !DISubprogram(name: "history_entry", scope: !113, file: !113, line: 2, type: !114, isLocal: true, isDefinition: true, scopeLine: 3, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!113 = !DIFile(filename: "history_entry.c", directory: "/work/history/ahci_xgene/runs/HIST-20261027T133810Z/h2")
!114 = !DISubroutineType(types: !115)
!115 = !{!25, !25}
!116 = !{}
!117 = !DILocalVariable(name: "acpi_handle_value", arg: 1, scope: !112, file: !113, line: 2, type: !25)
!118 = !DILocation(line: 2, column: 30, scope: !112)
!119 = !DILocation(line: 4, column: 39, scope: !112)
!120 = !DILocation(line: 4, column: 24, scope: !112)
!121 = !DILocation(line: 4, column: 22, scope: !112)
!122 = !DILocation(line: 5, column: 12, scope: !112)
!123 = !DILocation(line: 5, column: 5, scope: !112)
!124 = distinct !DISubprogram(name: "xgene_ahci_probe", scope: !125, file: !125, line: 750, type: !126, isLocal: true, isDefinition: true, scopeLine: 751, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!125 = !DIFile(filename: "drivers/ata/ahci_xgene.c", directory: "/work/history/ahci_xgene/runs/HIST-20261027T133810Z/h2")
!126 = !DISubroutineType(types: !127)
!127 = !{!25, !128}
!128 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !19, size: 64)
!129 = !DILocalVariable(name: "pdev", arg: 1, scope: !124, file: !125, line: 750, type: !128)
!130 = !DILocation(line: 750, column: 53, scope: !124)
!131 = !DILocalVariable(name: "dev", scope: !124, file: !125, line: 752, type: !53)
!132 = !DILocation(line: 752, column: 17, scope: !124)
!133 = !DILocation(line: 752, column: 24, scope: !124)
!134 = !DILocation(line: 752, column: 30, scope: !124)
!135 = !DILocalVariable(name: "hpriv", scope: !124, file: !125, line: 753, type: !51)
!136 = !DILocation(line: 753, column: 25, scope: !124)
!137 = !DILocalVariable(name: "ctx", scope: !124, file: !125, line: 754, type: !138)
!138 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !48, size: 64)
!139 = !DILocation(line: 754, column: 29, scope: !124)
!140 = !DILocalVariable(name: "res", scope: !124, file: !125, line: 755, type: !141)
!141 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !72, size: 64)
!142 = !DILocation(line: 755, column: 19, scope: !124)
!143 = !DILocalVariable(name: "of_devid", scope: !124, file: !125, line: 756, type: !144)
!144 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !78, size: 64)
!145 = !DILocation(line: 756, column: 29, scope: !124)
!146 = !DILocalVariable(name: "version", scope: !124, file: !125, line: 757, type: !5)
!147 = !DILocation(line: 757, column: 26, scope: !124)
!148 = !DILocalVariable(name: "ppi", scope: !124, file: !125, line: 758, type: !149)
!149 = !DICompositeType(tag: DW_TAG_array_type, baseType: !150, size: 128, elements: !57)
!150 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !28, size: 64)
!151 = !DILocation(line: 758, column: 30, scope: !124)
!152 = !DILocalVariable(name: "rc", scope: !124, file: !125, line: 760, type: !25)
!153 = !DILocation(line: 760, column: 6, scope: !124)
!154 = !DILocation(line: 762, column: 38, scope: !124)
!155 = !DILocation(line: 762, column: 10, scope: !124)
!156 = !DILocation(line: 762, column: 8, scope: !124)
!157 = !DILocation(line: 763, column: 6, scope: !158)
!158 = distinct !DILexicalBlock(scope: !124, file: !125, line: 763, column: 6)
!159 = !DILocation(line: 763, column: 6, scope: !124)
!160 = !DILocation(line: 764, column: 10, scope: !158)
!161 = !DILocation(line: 764, column: 3, scope: !158)
!162 = !DILocation(line: 766, column: 21, scope: !124)
!163 = !DILocation(line: 766, column: 8, scope: !124)
!164 = !DILocation(line: 766, column: 6, scope: !124)
!165 = !DILocation(line: 767, column: 7, scope: !166)
!166 = distinct !DILexicalBlock(scope: !124, file: !125, line: 767, column: 6)
!167 = !DILocation(line: 767, column: 6, scope: !124)
!168 = !DILocation(line: 768, column: 3, scope: !166)
!169 = !DILocation(line: 770, column: 21, scope: !124)
!170 = !DILocation(line: 770, column: 2, scope: !124)
!171 = !DILocation(line: 770, column: 9, scope: !124)
!172 = !DILocation(line: 770, column: 19, scope: !124)
!173 = !DILocation(line: 771, column: 15, scope: !124)
!174 = !DILocation(line: 771, column: 2, scope: !124)
!175 = !DILocation(line: 771, column: 7, scope: !124)
!176 = !DILocation(line: 771, column: 13, scope: !124)
!177 = !DILocation(line: 772, column: 13, scope: !124)
!178 = !DILocation(line: 772, column: 2, scope: !124)
!179 = !DILocation(line: 772, column: 7, scope: !124)
!180 = !DILocation(line: 772, column: 11, scope: !124)
!181 = !DILocation(line: 775, column: 30, scope: !124)
!182 = !DILocation(line: 775, column: 8, scope: !124)
!183 = !DILocation(line: 775, column: 6, scope: !124)
!184 = !DILocation(line: 776, column: 40, scope: !124)
!185 = !DILocation(line: 776, column: 45, scope: !124)
!186 = !DILocation(line: 776, column: 18, scope: !124)
!187 = !DILocation(line: 776, column: 2, scope: !124)
!188 = !DILocation(line: 776, column: 7, scope: !124)
!189 = !DILocation(line: 776, column: 16, scope: !124)
!190 = !DILocation(line: 777, column: 6, scope: !191)
!191 = distinct !DILexicalBlock(scope: !124, file: !125, line: 777, column: 6)
!192 = !DILocation(line: 777, column: 6, scope: !124)
!193 = !DILocation(line: 778, column: 10, scope: !191)
!194 = !DILocation(line: 778, column: 3, scope: !191)
!195 = !DILocation(line: 781, column: 30, scope: !124)
!196 = !DILocation(line: 781, column: 8, scope: !124)
!197 = !DILocation(line: 781, column: 6, scope: !124)
!198 = !DILocation(line: 782, column: 40, scope: !124)
!199 = !DILocation(line: 782, column: 45, scope: !124)
!200 = !DILocation(line: 782, column: 18, scope: !124)
!201 = !DILocation(line: 782, column: 2, scope: !124)
!202 = !DILocation(line: 782, column: 7, scope: !124)
!203 = !DILocation(line: 782, column: 16, scope: !124)
!204 = !DILocation(line: 783, column: 6, scope: !205)
!205 = distinct !DILexicalBlock(scope: !124, file: !125, line: 783, column: 6)
!206 = !DILocation(line: 783, column: 6, scope: !124)
!207 = !DILocation(line: 784, column: 10, scope: !205)
!208 = !DILocation(line: 784, column: 3, scope: !205)
!209 = !DILocation(line: 787, column: 30, scope: !124)
!210 = !DILocation(line: 787, column: 8, scope: !124)
!211 = !DILocation(line: 787, column: 6, scope: !124)
!212 = !DILocation(line: 788, column: 39, scope: !124)
!213 = !DILocation(line: 788, column: 44, scope: !124)
!214 = !DILocation(line: 788, column: 17, scope: !124)
!215 = !DILocation(line: 788, column: 2, scope: !124)
!216 = !DILocation(line: 788, column: 7, scope: !124)
!217 = !DILocation(line: 788, column: 15, scope: !124)
!218 = !DILocation(line: 789, column: 6, scope: !219)
!219 = distinct !DILexicalBlock(scope: !124, file: !125, line: 789, column: 6)
!220 = !DILocation(line: 789, column: 6, scope: !124)
!221 = !DILocation(line: 790, column: 10, scope: !219)
!222 = !DILocation(line: 790, column: 3, scope: !219)
!223 = !DILocation(line: 793, column: 30, scope: !124)
!224 = !DILocation(line: 793, column: 8, scope: !124)
!225 = !DILocation(line: 793, column: 6, scope: !124)
!226 = !DILocation(line: 794, column: 6, scope: !227)
!227 = distinct !DILexicalBlock(scope: !124, file: !125, line: 794, column: 6)
!228 = !DILocation(line: 794, column: 6, scope: !124)
!229 = !DILocalVariable(name: "csr", scope: !230, file: !125, line: 795, type: !15)
!230 = distinct !DILexicalBlock(scope: !227, file: !125, line: 794, column: 11)
!231 = !DILocation(line: 795, column: 17, scope: !230)
!232 = !DILocation(line: 795, column: 45, scope: !230)
!233 = !DILocation(line: 795, column: 50, scope: !230)
!234 = !DILocation(line: 795, column: 23, scope: !230)
!235 = !DILocation(line: 796, column: 7, scope: !236)
!236 = distinct !DILexicalBlock(scope: !230, file: !125, line: 796, column: 7)
!237 = !DILocation(line: 796, column: 7, scope: !230)
!238 = !DILocation(line: 797, column: 11, scope: !236)
!239 = !DILocation(line: 797, column: 4, scope: !236)
!240 = !DILocation(line: 799, column: 18, scope: !230)
!241 = !DILocation(line: 799, column: 3, scope: !230)
!242 = !DILocation(line: 799, column: 8, scope: !230)
!243 = !DILocation(line: 799, column: 16, scope: !230)
!244 = !DILocation(line: 800, column: 2, scope: !230)
!245 = !DILocation(line: 802, column: 50, scope: !124)
!246 = !DILocation(line: 802, column: 13, scope: !124)
!247 = !DILocation(line: 802, column: 11, scope: !124)
!248 = !DILocation(line: 803, column: 6, scope: !249)
!249 = distinct !DILexicalBlock(scope: !124, file: !125, line: 803, column: 6)
!250 = !DILocation(line: 803, column: 6, scope: !124)
!251 = !DILocation(line: 804, column: 7, scope: !252)
!252 = distinct !DILexicalBlock(scope: !253, file: !125, line: 804, column: 7)
!253 = distinct !DILexicalBlock(scope: !249, file: !125, line: 803, column: 16)
!254 = !DILocation(line: 804, column: 17, scope: !252)
!255 = !DILocation(line: 804, column: 7, scope: !253)
!256 = !DILocation(line: 805, column: 40, scope: !252)
!257 = !DILocation(line: 805, column: 50, scope: !252)
!258 = !DILocation(line: 805, column: 14, scope: !252)
!259 = !DILocation(line: 805, column: 12, scope: !252)
!260 = !DILocation(line: 805, column: 4, scope: !252)
!261 = !DILocation(line: 806, column: 2, scope: !253)
!262 = !DILocalVariable(name: "acpi_id", scope: !263, file: !125, line: 809, type: !264)
!263 = distinct !DILexicalBlock(scope: !249, file: !125, line: 808, column: 7)
!264 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !99, size: 64)
!265 = !DILocation(line: 809, column: 32, scope: !263)
!266 = !DILocalVariable(name: "info", scope: !263, file: !125, line: 810, type: !267)
!267 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !268, size: 64)
!268 = distinct !DICompositeType(tag: DW_TAG_structure_type, name: "acpi_device_info", file: !3, line: 46, size: 64, elements: !269)
!269 = !{!270, !271}
!270 = !DIDerivedType(tag: DW_TAG_member, name: "valid", scope: !268, file: !3, line: 46, baseType: !6, size: 32)
!271 = !DIDerivedType(tag: DW_TAG_member, name: "reserved", scope: !268, file: !3, line: 46, baseType: !6, size: 32, offset: 32)
!272 = !DILocation(line: 810, column: 28, scope: !263)
!273 = !DILocalVariable(name: "status", scope: !263, file: !125, line: 811, type: !274)
!274 = !DIDerivedType(tag: DW_TAG_typedef, name: "acpi_status", file: !3, line: 19, baseType: !25)
!275 = !DILocation(line: 811, column: 15, scope: !263)
!276 = !DILocation(line: 813, column: 55, scope: !263)
!277 = !DILocation(line: 813, column: 61, scope: !263)
!278 = !DILocation(line: 813, column: 13, scope: !263)
!279 = !DILocation(line: 813, column: 11, scope: !263)
!280 = !DILocation(line: 814, column: 8, scope: !281)
!281 = distinct !DILexicalBlock(scope: !263, file: !125, line: 814, column: 7)
!282 = !DILocation(line: 814, column: 7, scope: !263)
!283 = !DILocation(line: 815, column: 4, scope: !284)
!284 = distinct !DILexicalBlock(scope: !281, file: !125, line: 814, column: 17)
!285 = !DILocation(line: 816, column: 12, scope: !284)
!286 = !DILocation(line: 817, column: 3, scope: !284)
!287 = !DILocation(line: 817, column: 14, scope: !288)
!288 = distinct !DILexicalBlock(scope: !281, file: !125, line: 817, column: 14)
!289 = !DILocation(line: 817, column: 23, scope: !288)
!290 = !DILocation(line: 817, column: 14, scope: !281)
!291 = !DILocation(line: 818, column: 40, scope: !292)
!292 = distinct !DILexicalBlock(scope: !288, file: !125, line: 817, column: 36)
!293 = !DILocation(line: 818, column: 49, scope: !292)
!294 = !DILocation(line: 818, column: 14, scope: !292)
!295 = !DILocation(line: 818, column: 12, scope: !292)
!296 = !DILocation(line: 819, column: 34, scope: !292)
!297 = !DILocation(line: 819, column: 13, scope: !292)
!298 = !DILocation(line: 819, column: 11, scope: !292)
!299 = !DILocation(line: 820, column: 8, scope: !300)
!300 = distinct !DILexicalBlock(scope: !292, file: !125, line: 820, column: 8)
!301 = !DILocation(line: 820, column: 8, scope: !292)
!302 = !DILocation(line: 821, column: 5, scope: !303)
!303 = distinct !DILexicalBlock(scope: !300, file: !125, line: 820, column: 30)
!304 = !DILocation(line: 823, column: 13, scope: !303)
!305 = !DILocation(line: 824, column: 4, scope: !303)
!306 = !DILocation(line: 824, column: 15, scope: !307)
!307 = distinct !DILexicalBlock(scope: !300, file: !125, line: 824, column: 15)
!308 = !DILocation(line: 824, column: 21, scope: !307)
!309 = !DILocation(line: 824, column: 27, scope: !307)
!310 = !DILocation(line: 824, column: 15, scope: !300)
!311 = !DILocation(line: 825, column: 13, scope: !312)
!312 = distinct !DILexicalBlock(scope: !307, file: !125, line: 824, column: 45)
!313 = !DILocation(line: 826, column: 4, scope: !312)
!314 = !DILocation(line: 827, column: 3, scope: !292)
!315 = !DILocation(line: 831, column: 2, scope: !124)
!316 = !DILocation(line: 835, column: 34, scope: !317)
!317 = distinct !DILexicalBlock(scope: !124, file: !125, line: 835, column: 6)
!318 = !DILocation(line: 835, column: 12, scope: !317)
!319 = !DILocation(line: 835, column: 10, scope: !317)
!320 = !DILocation(line: 835, column: 6, scope: !124)
!321 = !DILocation(line: 836, column: 3, scope: !322)
!322 = distinct !DILexicalBlock(scope: !317, file: !125, line: 835, column: 41)
!323 = !DILocation(line: 837, column: 3, scope: !322)
!324 = !DILocation(line: 840, column: 34, scope: !325)
!325 = distinct !DILexicalBlock(scope: !124, file: !125, line: 840, column: 6)
!326 = !DILocation(line: 840, column: 6, scope: !325)
!327 = !DILocation(line: 840, column: 6, scope: !124)
!328 = !DILocation(line: 841, column: 3, scope: !329)
!329 = distinct !DILexicalBlock(scope: !325, file: !125, line: 840, column: 40)
!330 = !DILocation(line: 842, column: 3, scope: !329)
!331 = !DILocation(line: 846, column: 33, scope: !124)
!332 = !DILocation(line: 846, column: 7, scope: !124)
!333 = !DILocation(line: 846, column: 5, scope: !124)
!334 = !DILocation(line: 847, column: 6, scope: !335)
!335 = distinct !DILexicalBlock(scope: !124, file: !125, line: 847, column: 6)
!336 = !DILocation(line: 847, column: 6, scope: !124)
!337 = !DILocation(line: 848, column: 3, scope: !335)
!338 = !DILocation(line: 849, column: 29, scope: !124)
!339 = !DILocation(line: 849, column: 2, scope: !124)
!340 = !DILocation(line: 851, column: 38, scope: !124)
!341 = !DILocation(line: 851, column: 7, scope: !124)
!342 = !DILocation(line: 851, column: 5, scope: !124)
!343 = !DILocation(line: 852, column: 6, scope: !344)
!344 = distinct !DILexicalBlock(scope: !124, file: !125, line: 852, column: 6)
!345 = !DILocation(line: 852, column: 6, scope: !124)
!346 = !DILocation(line: 853, column: 3, scope: !344)
!347 = !DILocation(line: 856, column: 21, scope: !124)
!348 = !DILocation(line: 856, column: 2, scope: !124)
!349 = !DILocation(line: 859, column: 10, scope: !124)
!350 = !DILocation(line: 859, column: 2, scope: !124)
!351 = !DILocation(line: 861, column: 3, scope: !352)
!352 = distinct !DILexicalBlock(scope: !124, file: !125, line: 859, column: 19)
!353 = !DILocation(line: 861, column: 10, scope: !352)
!354 = !DILocation(line: 861, column: 16, scope: !352)
!355 = !DILocation(line: 862, column: 3, scope: !352)
!356 = !DILocation(line: 864, column: 3, scope: !352)
!357 = !DILocation(line: 864, column: 10, scope: !352)
!358 = !DILocation(line: 864, column: 16, scope: !352)
!359 = !DILocation(line: 865, column: 3, scope: !352)
!360 = !DILocation(line: 865, column: 10, scope: !352)
!361 = !DILocation(line: 865, column: 22, scope: !352)
!362 = !DILocation(line: 866, column: 3, scope: !352)
!363 = !DILocation(line: 868, column: 3, scope: !352)
!364 = !DILocation(line: 871, column: 31, scope: !124)
!365 = !DILocation(line: 871, column: 37, scope: !124)
!366 = !DILocation(line: 871, column: 48, scope: !124)
!367 = !DILocation(line: 871, column: 56, scope: !124)
!368 = !DILocation(line: 871, column: 44, scope: !124)
!369 = !DILocation(line: 871, column: 7, scope: !124)
!370 = !DILocation(line: 871, column: 5, scope: !124)
!371 = !DILocation(line: 873, column: 6, scope: !372)
!372 = distinct !DILexicalBlock(scope: !124, file: !125, line: 873, column: 6)
!373 = !DILocation(line: 873, column: 6, scope: !124)
!374 = !DILocation(line: 874, column: 3, scope: !372)
!375 = !DILocation(line: 876, column: 2, scope: !124)
!376 = !DILocation(line: 877, column: 2, scope: !124)
!377 = !DILocation(line: 880, column: 34, scope: !124)
!378 = !DILocation(line: 880, column: 2, scope: !124)
!379 = !DILocation(line: 881, column: 9, scope: !124)
!380 = !DILocation(line: 881, column: 2, scope: !124)
!381 = !DILocation(line: 882, column: 1, scope: !124)
!382 = distinct !DISubprogram(name: "history_entry_failure", scope: !113, file: !113, line: 15, type: !114, isLocal: true, isDefinition: true, scopeLine: 16, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!383 = !DILocalVariable(name: "acpi_handle_value", arg: 1, scope: !382, file: !113, line: 15, type: !25)
!384 = !DILocation(line: 15, column: 38, scope: !382)
!385 = !DILocation(line: 17, column: 9, scope: !386)
!386 = distinct !DILexicalBlock(scope: !382, file: !113, line: 17, column: 9)
!387 = !DILocation(line: 17, column: 27, scope: !386)
!388 = !DILocation(line: 17, column: 9, scope: !382)
!389 = !DILocation(line: 18, column: 9, scope: !386)
!390 = !DILocation(line: 19, column: 22, scope: !382)
!391 = !DILocation(line: 20, column: 12, scope: !382)
!392 = !DILocation(line: 20, column: 5, scope: !382)
!393 = !DILocation(line: 21, column: 1, scope: !382)
!394 = distinct !DISubprogram(name: "ahci_platform_get_resources", scope: !3, file: !3, line: 109, type: !395, isLocal: true, isDefinition: true, scopeLine: 110, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!395 = !DISubroutineType(types: !396)
!396 = !{!51, !128}
!397 = !DILocalVariable(name: "pdev", arg: 1, scope: !394, file: !3, line: 109, type: !128)
!398 = !DILocation(line: 109, column: 83, scope: !394)
!399 = !DILocation(line: 111, column: 11, scope: !394)
!400 = !DILocation(line: 112, column: 5, scope: !394)
!401 = distinct !DISubprogram(name: "devm_kzalloc", scope: !3, file: !3, line: 115, type: !402, isLocal: true, isDefinition: true, scopeLine: 116, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!402 = !DISubroutineType(types: !403)
!403 = !{!15, !53, !404, !6}
!404 = !DIDerivedType(tag: DW_TAG_typedef, name: "size_t", file: !405, line: 62, baseType: !11)
!405 = !DIFile(filename: "/opt/llvm7/lib/clang/7.0.0/include/stddef.h", directory: "/work/history/ahci_xgene/runs/HIST-20261027T133810Z/h2")
!406 = !DILocalVariable(name: "dev", arg: 1, scope: !401, file: !3, line: 115, type: !53)
!407 = !DILocation(line: 115, column: 42, scope: !401)
!408 = !DILocalVariable(name: "size", arg: 2, scope: !401, file: !3, line: 115, type: !404)
!409 = !DILocation(line: 115, column: 54, scope: !401)
!410 = !DILocalVariable(name: "flags", arg: 3, scope: !401, file: !3, line: 115, type: !6)
!411 = !DILocation(line: 115, column: 73, scope: !401)
!412 = !DILocation(line: 117, column: 11, scope: !401)
!413 = !DILocation(line: 118, column: 11, scope: !401)
!414 = !DILocation(line: 119, column: 11, scope: !401)
!415 = !DILocation(line: 120, column: 5, scope: !401)
!416 = distinct !DISubprogram(name: "platform_get_resource", scope: !3, file: !3, line: 123, type: !417, isLocal: true, isDefinition: true, scopeLine: 126, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!417 = !DISubroutineType(types: !418)
!418 = !{!141, !128, !6, !6}
!419 = !DILocalVariable(name: "pdev", arg: 1, scope: !416, file: !3, line: 123, type: !128)
!420 = !DILocation(line: 123, column: 71, scope: !416)
!421 = !DILocalVariable(name: "type", arg: 2, scope: !416, file: !3, line: 124, type: !6)
!422 = !DILocation(line: 124, column: 60, scope: !416)
!423 = !DILocalVariable(name: "num", arg: 3, scope: !416, file: !3, line: 125, type: !6)
!424 = !DILocation(line: 125, column: 60, scope: !416)
!425 = !DILocation(line: 127, column: 11, scope: !416)
!426 = !DILocation(line: 128, column: 11, scope: !416)
!427 = !DILocation(line: 129, column: 9, scope: !428)
!428 = distinct !DILexicalBlock(scope: !416, file: !3, line: 129, column: 9)
!429 = !DILocation(line: 129, column: 13, scope: !428)
!430 = !DILocation(line: 129, column: 9, scope: !416)
!431 = !DILocation(line: 130, column: 9, scope: !428)
!432 = !DILocation(line: 131, column: 5, scope: !416)
!433 = !DILocation(line: 132, column: 1, scope: !416)
!434 = distinct !DISubprogram(name: "devm_ioremap_resource", scope: !3, file: !3, line: 134, type: !435, isLocal: true, isDefinition: true, scopeLine: 135, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!435 = !DISubroutineType(types: !436)
!436 = !{!15, !53, !141}
!437 = !DILocalVariable(name: "dev", arg: 1, scope: !434, file: !3, line: 134, type: !53)
!438 = !DILocation(line: 134, column: 51, scope: !434)
!439 = !DILocalVariable(name: "res", arg: 2, scope: !434, file: !3, line: 134, type: !141)
!440 = !DILocation(line: 134, column: 73, scope: !434)
!441 = !DILocation(line: 136, column: 11, scope: !434)
!442 = !DILocation(line: 137, column: 11, scope: !434)
!443 = !DILocation(line: 138, column: 5, scope: !434)
!444 = distinct !DISubprogram(name: "of_match_device", scope: !3, file: !3, line: 141, type: !445, isLocal: true, isDefinition: true, scopeLine: 143, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!445 = !DISubroutineType(types: !446)
!446 = !{!144, !144, !447}
!447 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !448, size: 64)
!448 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !22)
!449 = !DILocalVariable(name: "matches", arg: 1, scope: !444, file: !3, line: 141, type: !144)
!450 = !DILocation(line: 141, column: 78, scope: !444)
!451 = !DILocalVariable(name: "dev", arg: 2, scope: !444, file: !3, line: 142, type: !447)
!452 = !DILocation(line: 142, column: 73, scope: !444)
!453 = !DILocation(line: 144, column: 11, scope: !444)
!454 = !DILocation(line: 145, column: 11, scope: !444)
!455 = !DILocation(line: 146, column: 5, scope: !444)
!456 = distinct !DISubprogram(name: "acpi_match_device", scope: !3, file: !3, line: 149, type: !457, isLocal: true, isDefinition: true, scopeLine: 151, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!457 = !DISubroutineType(types: !458)
!458 = !{!264, !264, !447}
!459 = !DILocalVariable(name: "ids", arg: 1, scope: !456, file: !3, line: 149, type: !264)
!460 = !DILocation(line: 149, column: 84, scope: !456)
!461 = !DILocalVariable(name: "dev", arg: 2, scope: !456, file: !3, line: 150, type: !447)
!462 = !DILocation(line: 150, column: 77, scope: !456)
!463 = !DILocation(line: 152, column: 11, scope: !456)
!464 = !DILocation(line: 153, column: 11, scope: !456)
!465 = !DILocation(line: 154, column: 5, scope: !456)
!466 = distinct !DISubprogram(name: "stub_log", scope: !3, file: !3, line: 99, type: !467, isLocal: true, isDefinition: true, scopeLine: 100, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!467 = !DISubroutineType(types: !468)
!468 = !{null, !469, null}
!469 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !470, size: 64)
!470 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !92)
!471 = !DILocalVariable(name: "fmt", arg: 1, scope: !466, file: !3, line: 99, type: !469)
!472 = !DILocation(line: 99, column: 34, scope: !466)
!473 = !DILocation(line: 101, column: 11, scope: !466)
!474 = !DILocation(line: 102, column: 1, scope: !466)
!475 = distinct !DISubprogram(name: "acpi_get_object_info", scope: !3, file: !3, line: 165, type: !476, isLocal: true, isDefinition: true, scopeLine: 167, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!476 = !DISubroutineType(types: !477)
!477 = !{!274, !478, !479}
!478 = !DIDerivedType(tag: DW_TAG_typedef, name: "acpi_handle", file: !3, line: 18, baseType: !11)
!479 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !267, size: 64)
!480 = !DILocalVariable(name: "handle", arg: 1, scope: !475, file: !3, line: 165, type: !478)
!481 = !DILocation(line: 165, column: 53, scope: !475)
!482 = !DILocalVariable(name: "out", arg: 2, scope: !475, file: !3, line: 166, type: !479)
!483 = !DILocation(line: 166, column: 67, scope: !475)
!484 = !DILocation(line: 174, column: 11, scope: !475)
!485 = !DILocation(line: 175, column: 11, scope: !475)
!486 = !DILocation(line: 176, column: 5, scope: !475)
!487 = distinct !DISubprogram(name: "xgene_ahci_mux_select", scope: !3, file: !3, line: 187, type: !488, isLocal: true, isDefinition: true, scopeLine: 188, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!488 = !DISubroutineType(types: !489)
!489 = !{!25, !138}
!490 = !DILocalVariable(name: "ctx", arg: 1, scope: !487, file: !3, line: 187, type: !138)
!491 = !DILocation(line: 187, column: 61, scope: !487)
!492 = !DILocation(line: 189, column: 11, scope: !487)
!493 = !DILocation(line: 190, column: 5, scope: !487)
!494 = distinct !DISubprogram(name: "xgene_ahci_is_memram_inited", scope: !3, file: !3, line: 193, type: !488, isLocal: true, isDefinition: true, scopeLine: 194, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!495 = !DILocalVariable(name: "ctx", arg: 1, scope: !494, file: !3, line: 193, type: !138)
!496 = !DILocation(line: 193, column: 67, scope: !494)
!497 = !DILocation(line: 195, column: 11, scope: !494)
!498 = !DILocation(line: 196, column: 5, scope: !494)
!499 = distinct !DISubprogram(name: "ahci_platform_enable_clks", scope: !3, file: !3, line: 199, type: !500, isLocal: true, isDefinition: true, scopeLine: 200, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!500 = !DISubroutineType(types: !501)
!501 = !{!25, !51}
!502 = !DILocalVariable(name: "hpriv", arg: 1, scope: !499, file: !3, line: 199, type: !51)
!503 = !DILocation(line: 199, column: 61, scope: !499)
!504 = !DILocation(line: 201, column: 11, scope: !499)
!505 = !DILocation(line: 202, column: 5, scope: !499)
!506 = distinct !DISubprogram(name: "ahci_platform_disable_clks", scope: !3, file: !3, line: 205, type: !507, isLocal: true, isDefinition: true, scopeLine: 206, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!507 = !DISubroutineType(types: !508)
!508 = !{null, !51}
!509 = !DILocalVariable(name: "hpriv", arg: 1, scope: !506, file: !3, line: 205, type: !51)
!510 = !DILocation(line: 205, column: 63, scope: !506)
!511 = !DILocation(line: 207, column: 11, scope: !506)
!512 = !DILocation(line: 208, column: 1, scope: !506)
!513 = distinct !DISubprogram(name: "ahci_platform_enable_resources", scope: !3, file: !3, line: 210, type: !500, isLocal: true, isDefinition: true, scopeLine: 211, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!514 = !DILocalVariable(name: "hpriv", arg: 1, scope: !513, file: !3, line: 210, type: !51)
!515 = !DILocation(line: 210, column: 66, scope: !513)
!516 = !DILocation(line: 212, column: 11, scope: !513)
!517 = !DILocation(line: 213, column: 5, scope: !513)
!518 = distinct !DISubprogram(name: "xgene_ahci_hw_init", scope: !3, file: !3, line: 221, type: !507, isLocal: true, isDefinition: true, scopeLine: 222, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!519 = !DILocalVariable(name: "hpriv", arg: 1, scope: !518, file: !3, line: 221, type: !51)
!520 = !DILocation(line: 221, column: 55, scope: !518)
!521 = !DILocation(line: 223, column: 11, scope: !518)
!522 = !DILocation(line: 224, column: 1, scope: !518)
!523 = distinct !DISubprogram(name: "xgene_ahci_irq_intr", scope: !3, file: !3, line: 92, type: !43, isLocal: true, isDefinition: true, scopeLine: 93, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!524 = !DILocalVariable(name: "irq", arg: 1, scope: !523, file: !3, line: 92, type: !25)
!525 = !DILocation(line: 92, column: 44, scope: !523)
!526 = !DILocalVariable(name: "dev_instance", arg: 2, scope: !523, file: !3, line: 92, type: !15)
!527 = !DILocation(line: 92, column: 55, scope: !523)
!528 = !DILocation(line: 94, column: 11, scope: !523)
!529 = !DILocation(line: 95, column: 11, scope: !523)
!530 = !DILocation(line: 96, column: 5, scope: !523)
!531 = distinct !DISubprogram(name: "ahci_platform_init_host", scope: !3, file: !3, line: 226, type: !532, isLocal: true, isDefinition: true, scopeLine: 230, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!532 = !DISubroutineType(types: !533)
!533 = !{!25, !128, !51, !150, !534}
!534 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !104, size: 64)
!535 = !DILocalVariable(name: "pdev", arg: 1, scope: !531, file: !3, line: 226, type: !128)
!536 = !DILocation(line: 226, column: 60, scope: !531)
!537 = !DILocalVariable(name: "hpriv", arg: 2, scope: !531, file: !3, line: 227, type: !51)
!538 = !DILocation(line: 227, column: 59, scope: !531)
!539 = !DILocalVariable(name: "pi", arg: 3, scope: !531, file: !3, line: 228, type: !150)
!540 = !DILocation(line: 228, column: 64, scope: !531)
!541 = !DILocalVariable(name: "sht", arg: 4, scope: !531, file: !3, line: 229, type: !534)
!542 = !DILocation(line: 229, column: 63, scope: !531)
!543 = !DILocation(line: 231, column: 11, scope: !531)
!544 = !DILocation(line: 232, column: 11, scope: !531)
!545 = !DILocation(line: 233, column: 11, scope: !531)
!546 = !DILocation(line: 234, column: 11, scope: !531)
!547 = !DILocation(line: 235, column: 5, scope: !531)
!548 = distinct !DISubprogram(name: "ahci_platform_disable_resources", scope: !3, file: !3, line: 216, type: !507, isLocal: true, isDefinition: true, scopeLine: 217, flags: DIFlagPrototyped, isOptimized: false, unit: !2, retainedNodes: !116)
!549 = !DILocalVariable(name: "hpriv", arg: 1, scope: !548, file: !3, line: 216, type: !51)
!550 = !DILocation(line: 216, column: 68, scope: !548)
!551 = !DILocation(line: 218, column: 11, scope: !548)
!552 = !DILocation(line: 219, column: 1, scope: !548)
