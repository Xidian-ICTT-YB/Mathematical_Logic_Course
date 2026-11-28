/*
 * Harness for the historical Linux driver function xgene_ahci_probe().
 *
 * The complete body of xgene_ahci_probe() below is copied from
 * drivers/ata/ahci_xgene.c at the pinned upstream commit.  The original driver
 * is GPL-2.0-or-later; its copyright and license header is preserved in the
 * provenance copies under history/ahci_xgene/source/.
 *
 * The surrounding declarations are a *documented environment model*, not the
 * Linux kernel.  Every stub is listed in history/ahci_xgene/HARNESS_MAPPING.md.
 * The KLEE entry point is history_entry(), which only supplies the ACPI handle
 * mode and then calls the real driver function.
 */
#include <stddef.h>
#include <stdint.h>

typedef uint32_t u32;
typedef unsigned long acpi_handle;
typedef int acpi_status;
typedef int irqreturn_t;

#define CONFIG_ACPI 1
#define ACPI_FAILURE(status) ((status) != 0)
#define AE_OK 0
#define AE_ERROR 1
#define ACPI_VALID_CID 1
#define ACPI_HANDLE(dev) (stub_acpi_handle)
#define __iomem
#define GFP_KERNEL 0
#define IORESOURCE_MEM 0x200
#define ENOMEM 12
#define ENODEV 19
#define AHCI_HFLAG_NO_NCQ (1u << 1)
#define AHCI_HFLAG_YES_FBS (1u << 2)
#define IS_ERR(ptr) ((uintptr_t)(ptr) >= (uintptr_t)-4095)
#define PTR_ERR(ptr) ((long)(ptr))

struct device { int unused; };
struct platform_device { struct device dev; };
struct resource { int unused; };
struct of_device_id { const void *data; };
struct acpi_device_id { char id[16]; unsigned long driver_data; };
/* Real struct acpi_device_info has many fields; the second field keeps this
 * stub structurally distinct from the unrelated `struct device` stub so LLVM
 * does not merge the two named types.  The driver only reads `valid`. */
struct acpi_device_info { unsigned int valid; unsigned int reserved; };
struct ahci_host_priv {
    void *mmio;
    void *plat_data;
    unsigned int flags;
    irqreturn_t (*irq_handler)(int, void *);
};
struct ata_port_info { int unused; };
struct scsi_host_template { int unused; };
struct ata_host { int unused; };

struct xgene_ahci_context {
    struct ahci_host_priv *hpriv;
    struct device *dev;
    unsigned char last_cmd[2];
    u32 class[2];
    void *csr_core;
    void *csr_diag;
    void *csr_axi;
    void *csr_mux;
};

enum xgene_ahci_version {
    XGENE_AHCI_V1 = 1,
    XGENE_AHCI_V2,
};

static const struct ata_port_info xgene_ahci_v1_port_info = { 1 };
static const struct ata_port_info xgene_ahci_v2_port_info = { 2 };
static struct scsi_host_template ahci_platform_sht = { 0 };
static const struct acpi_device_id xgene_ahci_acpi_match[] = {
    { "APMC0D0D", XGENE_AHCI_V1 },
    { "APMC0D32", XGENE_AHCI_V2 },
    { "", 0 },
};
static const struct of_device_id xgene_ahci_of_match[] = {
    { 0 },
};
static struct platform_device global_pdev;
static struct ahci_host_priv global_hpriv;
static struct xgene_ahci_context global_ctx;
static struct resource global_resource;
static struct acpi_device_info global_info;
static struct acpi_device_id global_acpi_id = { "APMC0D32", XGENE_AHCI_V2 };
static volatile unsigned long stub_acpi_handle = 0;

static irqreturn_t xgene_ahci_irq_intr(int irq, void *dev_instance)
{
    (void)irq;
    (void)dev_instance;
    return 0;
}

static void stub_log(const char *fmt, ...)
{
    (void)fmt;
}

#define dev_warn(dev, fmt, ...) stub_log(fmt, ##__VA_ARGS__)
#define dev_dbg(dev, fmt, ...) stub_log(fmt, ##__VA_ARGS__)
#define dev_err(dev, fmt, ...) stub_log(fmt, ##__VA_ARGS__)
#define dev_info(dev, fmt, ...) stub_log(fmt, ##__VA_ARGS__)

static struct ahci_host_priv *ahci_platform_get_resources(struct platform_device *pdev)
{
    (void)pdev;
    return &global_hpriv;
}

static void *devm_kzalloc(struct device *dev, size_t size, unsigned int flags)
{
    (void)dev;
    (void)size;
    (void)flags;
    return &global_ctx;
}

static struct resource *platform_get_resource(struct platform_device *pdev,
                                              unsigned int type,
                                              unsigned int num)
{
    (void)pdev;
    (void)type;
    if (num == 4)
        return NULL; /* optional mux resource is absent */
    return &global_resource;
}

static void *devm_ioremap_resource(struct device *dev, struct resource *res)
{
    (void)dev;
    (void)res;
    return (void *)0x1000;
}

static const struct of_device_id *of_match_device(const struct of_device_id *matches,
                                                   const struct device *dev)
{
    (void)matches;
    (void)dev;
    return NULL; /* force the ACPI device path */
}

static const struct acpi_device_id *acpi_match_device(const struct acpi_device_id *ids,
                                                       const struct device *dev)
{
    (void)ids;
    (void)dev;
    return &global_acpi_id; /* a valid ACPI ID with driver_data == V2 */
}

/*
 * Interface model for acpi_get_object_info().
 *
 * Linux contract used here: on success the function sets *out; on failure it
 * returns an error without promising that *out was written.  The two branches
 * are explicit so the analysis cannot assume that the output pointer is always
 * initialized.  See HARNESS_MAPPING.md.
 */
static acpi_status acpi_get_object_info(acpi_handle handle,
                                        struct acpi_device_info **out)
{
#ifdef HISTORY_ACPI_FAILURE_ONLY
    /*
     * Target-path build: the historical defect is the already-observed
     * acpi_get_object_info() failure path.  Selecting that path is an explicit
     * input-range restriction; it does not add an initialization or a read.
     */
    (void)handle;
    (void)out;
    return AE_ERROR; /* failure: *out is deliberately not written */
#else
    if (handle == 0) {
        return AE_ERROR; /* failure: *out is deliberately not written */
    }
    *out = &global_info;
    global_info.valid = 0;
    return AE_OK; /* success: output parameter written */
#endif
}

static int xgene_ahci_mux_select(struct xgene_ahci_context *ctx)
{
    (void)ctx;
    return 0;
}

static int xgene_ahci_is_memram_inited(struct xgene_ahci_context *ctx)
{
    (void)ctx;
    return 1; /* take the short skip_clk_phy path */
}

static int ahci_platform_enable_clks(struct ahci_host_priv *hpriv)
{
    (void)hpriv;
    return 0;
}

static void ahci_platform_disable_clks(struct ahci_host_priv *hpriv)
{
    (void)hpriv;
}

static int ahci_platform_enable_resources(struct ahci_host_priv *hpriv)
{
    (void)hpriv;
    return 0;
}

static void ahci_platform_disable_resources(struct ahci_host_priv *hpriv)
{
    (void)hpriv;
}

static void xgene_ahci_hw_init(struct ahci_host_priv *hpriv)
{
    (void)hpriv;
}

static int ahci_platform_init_host(struct platform_device *pdev,
                                   struct ahci_host_priv *hpriv,
                                   const struct ata_port_info *pi,
                                   struct scsi_host_template *sht)
{
    (void)pdev;
    (void)hpriv;
    (void)pi;
    (void)sht;
    return 0;
}

#line 750 "drivers/ata/ahci_xgene.c"
static int xgene_ahci_probe(struct platform_device *pdev)
{
	struct device *dev = &pdev->dev;
	struct ahci_host_priv *hpriv;
	struct xgene_ahci_context *ctx;
	struct resource *res;
	const struct of_device_id *of_devid;
	enum xgene_ahci_version version = XGENE_AHCI_V1;
	const struct ata_port_info *ppi[] = { &xgene_ahci_v1_port_info,
					      &xgene_ahci_v2_port_info };
	int rc;

	hpriv = ahci_platform_get_resources(pdev);
	if (IS_ERR(hpriv))
		return PTR_ERR(hpriv);

	ctx = devm_kzalloc(dev, sizeof(*ctx), GFP_KERNEL);
	if (!ctx)
		return -ENOMEM;

	hpriv->plat_data = ctx;
	ctx->hpriv = hpriv;
	ctx->dev = dev;

	/* Retrieve the IP core resource */
	res = platform_get_resource(pdev, IORESOURCE_MEM, 1);
	ctx->csr_core = devm_ioremap_resource(dev, res);
	if (IS_ERR(ctx->csr_core))
		return PTR_ERR(ctx->csr_core);

	/* Retrieve the IP diagnostic resource */
	res = platform_get_resource(pdev, IORESOURCE_MEM, 2);
	ctx->csr_diag = devm_ioremap_resource(dev, res);
	if (IS_ERR(ctx->csr_diag))
		return PTR_ERR(ctx->csr_diag);

	/* Retrieve the IP AXI resource */
	res = platform_get_resource(pdev, IORESOURCE_MEM, 3);
	ctx->csr_axi = devm_ioremap_resource(dev, res);
	if (IS_ERR(ctx->csr_axi))
		return PTR_ERR(ctx->csr_axi);

	/* Retrieve the optional IP mux resource */
	res = platform_get_resource(pdev, IORESOURCE_MEM, 4);
	if (res) {
		void __iomem *csr = devm_ioremap_resource(dev, res);
		if (IS_ERR(csr))
			return PTR_ERR(csr);

		ctx->csr_mux = csr;
	}

	of_devid = of_match_device(xgene_ahci_of_match, dev);
	if (of_devid) {
		if (of_devid->data)
			version = (enum xgene_ahci_version) of_devid->data;
	}
#ifdef CONFIG_ACPI
	else {
		const struct acpi_device_id *acpi_id;
		struct acpi_device_info *info;
		acpi_status status;

		acpi_id = acpi_match_device(xgene_ahci_acpi_match, &pdev->dev);
		if (!acpi_id) {
			dev_warn(&pdev->dev, "No node entry in ACPI table. Assume version1\n");
			version = XGENE_AHCI_V1;
		} else if (acpi_id->driver_data) {
			version = (enum xgene_ahci_version) acpi_id->driver_data;
			status = acpi_get_object_info(ACPI_HANDLE(&pdev->dev), &info);
			if (ACPI_FAILURE(status)) {
				dev_warn(&pdev->dev, "%s: Error reading device info. Assume version1\n",
					__func__);
				version = XGENE_AHCI_V1;
			} else if (info->valid & ACPI_VALID_CID) {
				version = XGENE_AHCI_V2;
			}
		}
	}
#endif

	dev_dbg(dev, "VAddr 0x%p Mmio VAddr 0x%p\n", ctx->csr_core,
		hpriv->mmio);

	/* Select ATA */
	if ((rc = xgene_ahci_mux_select(ctx))) {
		dev_err(dev, "SATA mux selection failed error %d\n", rc);
		return -ENODEV;
	}

	if (xgene_ahci_is_memram_inited(ctx)) {
		dev_info(dev, "skip clock and PHY initialization\n");
		goto skip_clk_phy;
	}

	/* Due to errata, HW requires full toggle transition */
	rc = ahci_platform_enable_clks(hpriv);
	if (rc)
		goto disable_resources;
	ahci_platform_disable_clks(hpriv);

	rc = ahci_platform_enable_resources(hpriv);
	if (rc)
		goto disable_resources;

	/* Configure the host controller */
	xgene_ahci_hw_init(hpriv);
skip_clk_phy:

	switch (version) {
	case XGENE_AHCI_V1:
		hpriv->flags = AHCI_HFLAG_NO_NCQ;
		break;
	case XGENE_AHCI_V2:
		hpriv->flags |= AHCI_HFLAG_YES_FBS;
		hpriv->irq_handler = xgene_ahci_irq_intr;
		break;
	default:
		break;
	}

	rc = ahci_platform_init_host(pdev, hpriv, ppi[version - 1],
				     &ahci_platform_sht);
	if (rc)
		goto disable_resources;

	dev_dbg(dev, "X-Gene SATA host controller initialized\n");
	return 0;

disable_resources:
	ahci_platform_disable_resources(hpriv);
	return rc;
}

#undef ACPI_HANDLE
#line 1 "history_entry.c"
__attribute__((used, noinline))
static int history_entry(int acpi_handle_value)
{
    stub_acpi_handle = (unsigned long)acpi_handle_value;
    return xgene_ahci_probe(&global_pdev);
}

/*
 * Failure-mode harness entry used by the historical KLEE run.  The real Linux
 * bug is the acpi_get_object_info() failure path; restricting the harness to
 * handle == 0 makes that path the only one that enters the driver.  This is an
 * explicit input-range restriction, not a change to xgene_ahci_probe().
 */
__attribute__((used, noinline))
static int history_entry_failure(int acpi_handle_value)
{
    if (acpi_handle_value != 0)
        return 0;
    stub_acpi_handle = 0;
    return xgene_ahci_probe(&global_pdev);
}
