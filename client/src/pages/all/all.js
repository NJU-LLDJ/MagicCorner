// pages/try/try.js

var books_data = require("../../res/data/books.js")
Page({

  /**
   * 页面的初始数据
   */
  data: {
    books : []
  },

  ToSearch () {
    wx.navigateTo({
      url: '../search/search',
    })
  },

  ToDetail(e) {
    wx.navigateTo ({
      url: '../detail/detail?item=' + encodeURIComponent(JSON.stringify(e.currentTarget.dataset.item))
    })
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad(options) {
    this.setData ({
      books : books_data.BookList
    })
    // wx.request({
    //   url: 'http://101.133.154.219:8000/api/v1/user/1234',
    //   method:"GET",
    //   data : {
    //     d : "杰宝"
    //   },
    //   success: (res) => {
    //     console.log(res.data)
    //   },
    //   fail:(res) => {
    //     console.log("fail")
    //   }
    // })
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady() {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow() {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide() {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload() {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
  onPullDownRefresh() {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom() {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage() {

  }
})