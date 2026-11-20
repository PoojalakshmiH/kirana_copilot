import streamlit as st
import pandas as pd
from datetime import date
import uuid

st.set_page_config(page_title="Kirana Copilot", page_icon="🛒", layout="wide")

DEFAULT_DATA = [
    {"product":"Fortune Oil 1L","stock":4,"min_stock":15,"target_stock":20,"unit_price":135,"expiry_days":90,"daily_sales":3},
    {"product":"Rice 25kg","stock":2,"min_stock":5,"target_stock":6,"unit_price":1050,"expiry_days":180,"daily_sales":1},
    {"product":"Jaggery 1kg","stock":5,"min_stock":10,"target_stock":35,"unit_price":46,"expiry_days":60,"daily_sales":4},
    {"product":"Tata Salt 1kg","stock":8,"min_stock":12,"target_stock":25,"unit_price":22,"expiry_days":240,"daily_sales":5},
    {"product":"Maggi 70g","stock":42,"min_stock":20,"target_stock":50,"unit_price":14,"expiry_days":12,"daily_sales":7},
    {"product":"Parle-G","stock":12,"min_stock":15,"target_stock":30,"unit_price":20,"expiry_days":120,"daily_sales":6},
    {"product":"Rusk","stock":18,"min_stock":10,"target_stock":20,"unit_price":25,"expiry_days":5,"daily_sales":2},
    {"product":"Milk 500ml","stock":6,"min_stock":10,"target_stock":15,"unit_price":30,"expiry_days":2,"daily_sales":10},
    {"product":"Sugar 1kg","stock":10,"min_stock":15,"target_stock":25,"unit_price":45,"expiry_days":150,"daily_sales":4},
    {"product":"Toor Dal 1kg","stock":7,"min_stock":12,"target_stock":20,"unit_price":130,"expiry_days":100,"daily_sales":2},
]

if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame(DEFAULT_DATA)
if "budget" not in st.session_state:
    st.session_state.budget = 10000
if "orders" not in st.session_state:
    st.session_state.orders = []
if "draft" not in st.session_state:
    st.session_state.draft = None

df = st.session_state.inventory.copy()
df["status"] = df.apply(
    lambda r: "Expiring soon" if r["expiry_days"] <= 7 else
    ("Low stock" if r["stock"] < r["min_stock"] else "Healthy"), axis=1
)
st.sidebar.title("🛒 Kirana Copilot")
page = st.sidebar.radio("Navigate", ["Dashboard", "Inventory", "Expiry Guard", "Smart Order", "Order History"])
st.sidebar.markdown("---")
st.sidebar.caption("Hackathon prototype · Demo data · No real orders are sent")

def build_draft(budget):
    inv=st.session_state.inventory.copy()
    recommendations=[]
    # Prioritize products that are below minimum; avoid replenishing near-expiry products.
    candidates=inv[(inv["stock"] < inv["min_stock"]) & (inv["expiry_days"] > 7)].copy()
    candidates["gap"]=candidates["target_stock"]-candidates["stock"]
    candidates["gap"]=candidates["gap"].clip(lower=0)
    candidates["priority"]=candidates["daily_sales"]/(candidates["stock"]+1)
    candidates=candidates.sort_values("priority",ascending=False)
    remaining=float(budget)
    for _,r in candidates.iterrows():
        qty=int(r["gap"])
        # Respect the budget: choose a quantity that can be afforded.
        affordable=int(remaining//r["unit_price"]) if r["unit_price"]>0 else qty
        qty=min(qty,affordable)
        if qty>0:
            cost=qty*float(r["unit_price"])
            recommendations.append({"product":r["product"],"current_stock":int(r["stock"]),
                "quantity":qty,"unit_price":float(r["unit_price"]),"cost":cost,
                "reason":f"Stock ({int(r['stock'])}) is below minimum ({int(r['min_stock'])}); replenishing toward target."})
            remaining-=cost
    return recommendations

def total_order(items):
    return sum(float(x["quantity"])*float(x["unit_price"]) for x in items)

if page=="Dashboard":
    st.title("Good morning, Sharma Kirana 👋")
    st.subheader("Your shop at a glance")
    total_items=len(df)
    low=int((df["stock"]<df["min_stock"]).sum())
    expiry=int((df["expiry_days"]<=7).sum())
    planned=total_order(st.session_state.draft or [])
    a,b,c,d=st.columns(4)
    a.metric("Products tracked",total_items)
    b.metric("Low-stock items",low)
    c.metric("Expiring within 7 days",expiry)
    d.metric("Cash budget",f"₹{st.session_state.budget:,.0f}")
    st.markdown("### Stock overview")
    st.dataframe(df[["product","stock","min_stock","expiry_days","unit_price","status"]],hide_index=True,use_container_width=True)
    left,right=st.columns(2)
    with left:
        st.markdown("### Low-stock products")
        st.dataframe(df[df["stock"]<df["min_stock"]][["product","stock","min_stock"]],hide_index=True,use_container_width=True)
    with right:
        st.markdown("### Expiring soon")
        st.dataframe(df[df["expiry_days"]<=7][["product","stock","expiry_days"]],hide_index=True,use_container_width=True)
    if st.button("✨ Generate my smart order",type="primary",use_container_width=True):
        st.session_state.draft=build_draft(st.session_state.budget)
        st.success("Order draft generated. Open Smart Order to review it.")

elif page=="Inventory":
    st.title("📦 Inventory")
    st.write("Edit demo inventory values below. Changes persist for this session.")
    edited=st.data_editor(st.session_state.inventory,hide_index=True,num_rows="dynamic",use_container_width=True,
        column_config={"product":st.column_config.TextColumn(),"stock":st.column_config.NumberColumn(min_value=0,step=1),
        "min_stock":st.column_config.NumberColumn(min_value=0,step=1),"target_stock":st.column_config.NumberColumn(min_value=0,step=1),
        "unit_price":st.column_config.NumberColumn(min_value=0),"expiry_days":st.column_config.NumberColumn(min_value=0,step=1),
        "daily_sales":st.column_config.NumberColumn(min_value=0,step=1)})
    if st.button("Save inventory",type="primary"):
        st.session_state.inventory=edited
        st.session_state.draft=None
        st.success("Inventory saved. Generate a fresh order draft to use these changes.")

elif page=="Expiry Guard":
    st.title("⚠️ Expiry Guard")
    st.write("Demo expiry-risk rules: 7 days or less = urgent; 8–15 days = watch.")
    inv=st.session_state.inventory.copy()
    inv["expiry_alert"]=inv["expiry_days"].apply(lambda x:"🔴 Urgent" if x<=7 else ("🟠 Watch" if x<=15 else "🟢 OK"))
    risky=inv[inv["expiry_days"]<=15].sort_values("expiry_days")
    if risky.empty:
        st.success("No products within the 15-day alert window.")
    else:
        st.dataframe(risky[["product","stock","expiry_days","expiry_alert"]],hide_index=True,use_container_width=True)
        for _,r in risky.iterrows():
            if r["expiry_days"]<=7:
                st.warning(f"**{r['product']}**: {int(r['stock'])} in stock, {int(r['expiry_days'])} day(s) left. Suggested action: prioritize selling; avoid a new order until stock is reviewed.")
            else:
                st.info(f"**{r['product']}**: {int(r['stock'])} in stock, {int(r['expiry_days'])} days left. Suggested action: monitor.")

elif page=="Smart Order":
    st.title("🧠 Smart Order")
    st.number_input("Available purchasing budget (₹)",min_value=0,value=int(st.session_state.budget),step=500,key="budget_input")
    if st.button("Generate / refresh recommendation",type="primary"):
        st.session_state.budget=int(st.session_state.budget_input)
        st.session_state.draft=build_draft(st.session_state.budget)
    # Sync budget if input was changed
    st.session_state.budget=int(st.session_state.budget_input)
    if st.session_state.draft is None:
        st.info("Generate a recommendation to begin. The system will prioritize low-stock products and avoid replenishing products expiring within 7 days.")
    else:
        items=st.session_state.draft
        if not items:
            st.warning("No eligible reorder items were found within this budget.")
        else:
            st.caption("Recommendations are rules-based in this prototype. All orders require owner approval.")
            for i,item in enumerate(items):
                cols=st.columns([3,1,1,1,1])
                cols[0].markdown(f"**{item['product']}**")
                cols[1].write(f"Stock: {item['current_stock']}")
                new_qty=cols[2].number_input("Qty",min_value=0,value=int(item["quantity"]),step=1,key=f"qty_{i}")
                cols[3].write(f"₹{item['unit_price']:,.0f}/unit")
                cols[4].write(f"₹{new_qty*item['unit_price']:,.0f}")
                item["quantity"]=new_qty
                item["cost"]=new_qty*item["unit_price"]
                st.caption(item["reason"])
            items=[x for x in items if x["quantity"]>0]
            st.session_state.draft=items
            total=total_order(items)
            rem=st.session_state.budget-total
            x,y,z=st.columns(3)
            x.metric("Order total",f"₹{total:,.0f}")
            y.metric("Budget",f"₹{st.session_state.budget:,.0f}")
            z.metric("Remaining",f"₹{rem:,.0f}")
            if total>st.session_state.budget:
                st.error("Order is over budget. Reduce quantities before approval.")
            elif st.button("✅ Approve demo order",type="primary",use_container_width=True):
                order={"order_id":"KC-"+uuid.uuid4().hex[:6].upper(),"date":str(date.today()),
                    "items":[dict(x) for x in items],"total":total,"status":"Approved (demo)"}
                st.session_state.orders.insert(0,order)
                st.session_state.draft=None
                st.success(f"Approved! Demo order {order['order_id']} recorded. No real order was sent.")
                st.balloons()
            if st.button("Discard draft"):
                st.session_state.draft=None
                st.rerun()

elif page=="Order History":
    st.title("🧾 Order History")
    if not st.session_state.orders:
        st.info("No approved demo orders yet. Generate and approve an order to see it here.")
    else:
        for order in st.session_state.orders:
            with st.expander(f"{order['order_id']} · {order['date']} · ₹{order['total']:,.0f} · {order['status']}"):
                st.dataframe(pd.DataFrame(order["items"]),hide_index=True,use_container_width=True)

st.markdown("---")
st.caption("Kirana Copilot · Hackathon prototype · Illustrative data only · Orders are not sent to suppliers.")
